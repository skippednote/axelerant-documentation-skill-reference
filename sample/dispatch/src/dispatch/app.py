"""API + SQLite work queue + local receipt adapter, using only the standard library.

Accepted work is retried at least once, with a bounded attempt count. A provider
receipt can be duplicated if a process dies after writing it and before recording
success. Leases prevent a routine status read from resetting active work.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

CHANNELS = {'email','sms','push'}
MAX_ATTEMPTS = 3


class Store:
    def __init__(self,path: Path,clock=time.time):
        self.path=Path(path); self.clock=clock

    @contextmanager
    def connection(self):
        con=sqlite3.connect(self.path,timeout=5)
        con.row_factory=sqlite3.Row
        try:
            with con: yield con
        finally: con.close()

    def init(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connection() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY, channel TEXT NOT NULL, recipient TEXT NOT NULL,
                body TEXT NOT NULL, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                available REAL NOT NULL, lease REAL, claim TEXT, error TEXT)''')

    def enqueue(self,channel,recipient,body):
        if not all(isinstance(v,str) for v in (channel,recipient,body)):
            raise ValueError('channel, recipient and body must be strings')
        if channel not in CHANNELS or not recipient.strip() or not body.strip():
            raise ValueError('unsupported channel or empty recipient/body')
        mid=str(uuid.uuid4())
        with self.connection() as c:
            c.execute('INSERT INTO messages(id,channel,recipient,body,status,available) VALUES(?,?,?,?,?,?)',
                      (mid,channel,recipient,body,'queued',self.clock()))
        return self.get(mid)

    def get(self,mid):
        with self.connection() as c: row=c.execute('SELECT * FROM messages WHERE id=?',(mid,)).fetchone()
        return dict(row) if row else None

    def counts(self):
        result={k:0 for k in ('queued','processing','sent','failed')}
        with self.connection() as c:
            for row in c.execute('SELECT status,COUNT(*) AS n FROM messages GROUP BY status'):
                result[row['status']]=row['n']
        return result

    def claim(self,lease_seconds=30):
        if lease_seconds<=0: raise ValueError('lease_seconds must be positive')
        now=self.clock(); token=str(uuid.uuid4())
        with self.connection() as c:
            c.execute('BEGIN IMMEDIATE')
            # Only expired leases become claimable. Initialization and reads do not reset work.
            c.execute("UPDATE messages SET status=CASE WHEN attempts>=? THEN 'failed' ELSE 'queued' END, claim=NULL,lease=NULL WHERE status='processing' AND lease<=?",(MAX_ATTEMPTS,now))
            row=c.execute("SELECT id FROM messages WHERE status='queued' AND available<=? AND attempts<? ORDER BY available,id LIMIT 1",(now,MAX_ATTEMPTS)).fetchone()
            if not row: return None
            c.execute("UPDATE messages SET status='processing',attempts=attempts+1,claim=?,lease=? WHERE id=?",(token,now+lease_seconds,row['id']))
            return dict(c.execute('SELECT * FROM messages WHERE id=?',(row['id'],)).fetchone())

    def finish(self,message,error=None):
        status='sent' if error is None else ('failed' if message['attempts']>=MAX_ATTEMPTS else 'queued')
        with self.connection() as c:
            return c.execute('''UPDATE messages SET status=?,error=?,available=?,lease=NULL,claim=NULL
                                WHERE id=? AND status='processing' AND claim=?''',
                             (status,error,self.clock()+2**message['attempts'],message['id'],message['claim'])).rowcount==1


def work_once(store: Store,outbox: Path):
    msg=store.claim()
    if not msg: return False
    if msg['recipient'].startswith('fail:'):
        store.finish(msg,'simulated provider rejection')
    else:
        outbox.parent.mkdir(parents=True,exist_ok=True)
        # One append syscall per receipt; the adapter deliberately does not deduplicate.
        receipt=json.dumps({'message_id':msg['id'],'channel':msg['channel'],'recipient':msg['recipient']})+'\n'
        fd=os.open(outbox,os.O_CREAT|os.O_APPEND|os.O_WRONLY,0o600)
        try: os.write(fd,receipt.encode())
        finally: os.close(fd)
        store.finish(msg)
    return True


def server(store: Store,port=8080):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def reply(self,status,payload):
            data=json.dumps(payload).encode()
            self.send_response(status); self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            path=urlsplit(self.path).path
            if path=='/healthz':
                try: store.counts()
                except sqlite3.Error: self.reply(503,{'status':'database unavailable'})
                else: self.reply(200,{'status':'ok'})
            elif path=='/metrics': self.reply(200,store.counts())
            elif path.startswith('/v1/messages/'):
                msg=store.get(path.rsplit('/',1)[-1]); self.reply(200 if msg else 404,msg or {'error':'not found'})
            else: self.reply(404,{'error':'not found'})
        def do_POST(self):
            if urlsplit(self.path).path!='/v1/messages': self.reply(404,{'error':'not found'}); return
            try:
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<=65536: raise ValueError('body must be 1–65536 bytes')
                self.connection.settimeout(5)
                payload=json.loads(self.rfile.read(n))
                if not isinstance(payload,dict): raise ValueError('body must be a JSON object')
                msg=store.enqueue(payload.get('channel'),payload.get('recipient'),payload.get('body'))
            except (ValueError,TimeoutError) as e: self.reply(400,{'error':str(e)}); return
            self.reply(202,{'id':msg['id'],'status':'queued'})
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--state',type=Path,default=Path(os.getenv('DISPATCH_STATE','.state')))
    subs=p.add_subparsers(dest='command',required=True)
    for name in ('init','status','worker-once'): subs.add_parser(name)
    api=subs.add_parser('api'); api.add_argument('--port',type=int,default=8080)
    worker=subs.add_parser('worker')
    send=subs.add_parser('send'); send.add_argument('--recipient',default='reader@example.test')
    get=subs.add_parser('get'); get.add_argument('id')
    args=p.parse_args(); store=Store(args.state/'dispatch.sqlite'); store.init()
    if args.command=='init': print(store.path)
    elif args.command=='status': print(json.dumps(store.counts(),sort_keys=True))
    elif args.command=='send': print(json.dumps(store.enqueue('email',args.recipient,'Hello')))
    elif args.command=='get': print(json.dumps(store.get(args.id)))
    elif args.command=='worker-once': print(work_once(store,args.state/'outbox.jsonl'))
    elif args.command=='worker':
        try:
            while True:
                if not work_once(store,args.state/'outbox.jsonl'): time.sleep(.25)
        except KeyboardInterrupt: pass
    elif args.command=='api':
        http=server(store,args.port)
        print(f'http://127.0.0.1:{http.server_port}',flush=True)
        try: http.serve_forever()
        except KeyboardInterrupt: pass
        finally: http.server_close()
    return 0

if __name__=='__main__': raise SystemExit(main())
