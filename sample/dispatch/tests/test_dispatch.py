import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from dispatch.app import Store,work_once,server

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); self.now=[100.0]
        self.store=Store(self.root/'db',clock=lambda:self.now[0]); self.store.init()
    def test_deliver(self):
        msg=self.store.enqueue('email','reader@example.test','hello')
        self.assertTrue(work_once(self.store,self.root/'out'))
        self.assertEqual(self.store.get(msg['id'])['status'],'sent')
        self.assertEqual(json.loads((self.root/'out').read_text())['message_id'],msg['id'])
    def test_retry_limit(self):
        msg=self.store.enqueue('sms','fail:test','hello')
        for i in range(3):
            self.assertTrue(work_once(self.store,self.root/'out')); self.now[0]+=10
        self.assertEqual(self.store.get(msg['id'])['status'],'failed')
        self.assertFalse(work_once(self.store,self.root/'out'))
    def test_initialization_does_not_reset_active_claim(self):
        self.store.enqueue('push','device','hello'); claim=self.store.claim()
        self.store.init(); self.store.counts()
        self.assertIsNone(self.store.claim()); self.assertTrue(self.store.finish(claim))
    def test_expired_lease_recovery_and_stale_worker(self):
        self.store.enqueue('email','reader','hello'); old=self.store.claim()
        self.now[0]+=31; new=self.store.claim()
        self.assertIsNotNone(new); self.assertFalse(self.store.finish(old)); self.assertTrue(self.store.finish(new))
    def test_no_duplicate_concurrent_claim(self):
        self.store.enqueue('email','reader','hello'); results=[]
        ts=[threading.Thread(target=lambda:results.append(self.store.claim())) for _ in range(4)]
        for t in ts:t.start()
        for t in ts:t.join()
        self.assertEqual(sum(r is not None for r in results),1)
    def test_bad_fields(self):
        for payload in [('fax','reader','body'),('email','','body'),('email',{},'body')]:
            with self.assertRaises(ValueError): self.store.enqueue(*payload)
    def test_http_roundtrip(self):
        http=server(self.store,0); t=threading.Thread(target=http.serve_forever,daemon=True);t.start()
        try:
            base=f'http://127.0.0.1:{http.server_port}'
            req=Request(base+'/v1/messages',data=json.dumps({'channel':'email','recipient':'reader','body':'hi'}).encode(),headers={'Content-Type':'application/json'})
            with urlopen(req,timeout=3) as response:
                self.assertEqual(response.status,202); mid=json.load(response)['id']
            work_once(self.store,self.root/'out')
            with urlopen(base+'/v1/messages/'+mid,timeout=3) as response:self.assertEqual(json.load(response)['status'],'sent')
            with self.assertRaises(HTTPError) as err: urlopen(Request(base+'/v1/messages',data=b'[]'),timeout=3)
            self.assertEqual(err.exception.code,400)
        finally: http.shutdown();http.server_close();t.join()

if __name__=='__main__': unittest.main()

class RunbookDrills(unittest.TestCase):
    setUp = Tests.setUp
    def test_queue_alert_drill(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
        from check_alerts import evaluate
        for i in range(51): self.store.enqueue('email',f'reader{i}','hello')
        self.assertIn('DispatchQueueDepthCritical',evaluate(self.store.counts()))
        while work_once(self.store,self.root/'out'): pass
        self.assertNotIn('DispatchQueueDepthCritical',evaluate(self.store.counts()))
        self.assertEqual(self.store.counts()['sent'],51)
    def test_provider_alert_drill(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
        from check_alerts import evaluate
        for i in range(18): self.store.enqueue('email',f'reader{i}','hello')
        for i in range(2): self.store.enqueue('email',f'fail:{i}','hello')
        for i in range(3):
            while work_once(self.store,self.root/'out'): pass
            self.now[0]+=10
        self.assertIn('ProviderErrorRateHigh',evaluate(self.store.counts()))
        good=self.store.enqueue('email','normal','hello')
        self.assertTrue(work_once(self.store,self.root/'out'))
        self.assertEqual(self.store.get(good['id'])['status'],'sent')
