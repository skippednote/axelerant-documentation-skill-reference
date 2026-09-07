"""Evaluate the two local exercise alerts. This does not send real pages."""
import json
import os
from pathlib import Path
from dispatch.app import Store


def evaluate(counts):
    active=[]
    if counts['queued']>50: active.append('DispatchQueueDepthCritical')
    total=counts['sent']+counts['failed']
    if total>=20 and counts['failed']/total>0.05: active.append('ProviderErrorRateHigh')
    return active

if __name__=='__main__':
    store=Store(Path(os.getenv('DISPATCH_STATE','.state'))/'dispatch.sqlite'); store.init()
    print(json.dumps(evaluate(store.counts())))
