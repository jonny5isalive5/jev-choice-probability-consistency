"""Authorized continuation: replay saved calls locally; send only the unmade suffix.

Original failures and files are immutable. Derived merged ledger retains the
original stopped event and appends an explicitly labelled R1 revalidation receipt.
"""
import hashlib
import itertools
import json
import os
import shutil
from collections import Counter
from decimal import Decimal
from pathlib import Path
from jev import Client,HTTPTransport,Stop,canonical,validate,probability_mass_policy,RATE_USD,CALL_RESERVE
from pilot import run_arm,verify_freeze
from secure_credential import credential

ROOT=Path(__file__).parent
BASE=Path('evidence/Jev-Live-JL-002-R1')
OUT=BASE/'evidence/continued-run-001'


def read_parent():
    manifest=json.loads((ROOT/'parent.json').read_text())
    for name,expected in manifest['files'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected:
            raise Stop('parent source or evidence changed')
    path=Path(manifest['run'])
    ledger=[json.loads(x) for x in (path/'ledger.jsonl').read_text().splitlines()]
    reserved={r['sequence']:r for r in ledger if r['event']=='reserved'}
    received={r['sequence']:r for r in ledger if r['event']=='received'}
    valid={r['sequence'] for r in ledger if r['event']=='validated'}
    failures=[r for r in ledger if r['event']=='stopped']
    if set(reserved)!=set(range(1,222)) or set(received)!=set(reserved) or valid!=set(range(1,221)):
        raise Stop('parent request accounting differs from frozen recovery plan')
    if len(failures)!=1 or failures[0]['sequence']!=221 or failures[0]['reason']!='probabilities do not sum to one':
        raise Stop('parent failure differs from frozen recovery plan')
    cache={};responses={};total=Decimal(0)
    for seq,event in reserved.items():
        raw=(path/f'response-{seq:04}.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=received[seq]['response_sha256']:
            raise Stop('parent response hash mismatch')
        response=validate(json.loads(raw),event['request'])
        responses[seq]=response
        identity=(event['case_id'],event['arm'],event['stage'])
        cache[identity]={'request':event['request'],'response':response,'sequence':seq}
        total+=Decimal(response['usage']['input_tokens'])*RATE_USD
    if probability_mass_policy(responses[221]['answers']['decision']['probabilities'])!='hundredth_rounding_compatible_values_unchanged':
        raise Stop('saved failed response is not the expected rounding case')
    seal=json.loads((path/'prediction-seal.json').read_text())
    if hashlib.sha256((path/'predictions.jsonl').read_bytes()).hexdigest()!=seal['sha256']:
        raise Stop('parent prediction seal mismatch')
    predictions=[json.loads(x) for x in (path/'predictions.jsonl').read_text().splitlines()]
    if len(predictions)!=73 or seal['count']!=73:raise Stop('parent completed prediction count mismatch')
    return path,ledger,reserved,cache,responses,total,predictions


class ContinueClient:
    def __init__(self,client,cache,schedule):
        self.client,self.cache,self.schedule=client,cache,schedule
        self.replayed=[]
    def call(self,request,cid,arm,stage):
        identity=(cid,arm,stage)
        if identity in self.cache:
            saved=self.cache[identity]
            if canonical(request)!=canonical(saved['request']):raise Stop('replayed request differs from original')
            self.replayed.append(saved['sequence'])
            return saved['response']['answers']
        if self.client.calls>=len(self.schedule) or identity!=self.schedule[self.client.calls]:
            raise Stop('new call is not the next unmade request')
        return self.client.call(request,cid,arm,stage)


def execute():
    verify_freeze()
    old,ledger,reserved,cache,responses,parent_cost,old_predictions=read_parent()
    readiness=json.loads((BASE/'evidence/readiness.json').read_text())
    if not readiness.get('authenticated_models_access'):raise Stop('authenticated readiness missing')
    secret=credential()
    if not secret:raise Stop('authorized named credential missing')
    cases=json.loads((ROOT/'cases.json').read_text());prompts=json.loads((ROOT/'prompts.json').read_text())
    arms=list(itertools.permutations(('single','swarm','sequential')))
    checklists=list(itertools.permutations(range(3)))
    schedule=[('SMOKE','smoke',0)]
    for i,case in enumerate(cases):
        for arm in arms[i%6]:
            schedule.extend((case['id'],arm,stage) for stage in range(1 if arm=='single' else 4))
    if len(schedule)!=865:raise Stop('frozen schedule length changed')
    for seq,event in reserved.items():
        if (event['case_id'],event['arm'],event['stage'])!=schedule[seq-1]:raise Stop('parent schedule mismatch')
    client=Client(HTTPTransport(secret),OUT)
    shutil.copy2(old/'ledger.jsonl',OUT/'ledger.jsonl')
    shutil.copy2(old/'predictions.jsonl',OUT/'predictions.jsonl')
    for seq in reserved:shutil.copy2(old/f'response-{seq:04}.json',OUT/f'response-{seq:04}.json')
    client.calls=221;client.reserved=CALL_RESERVE*221;client.actual_usd=parent_cost
    client.arm_calls=Counter((r['case_id'],r['arm']) for r in reserved.values())
    event=reserved[221]
    identity={k:event[k] for k in ('sequence','case_id','arm','stage')}
    client.append(dict(identity,event='revalidation_receipt',revision='JL-002-R1',
                       original_failure_unchanged=True,source=str(old/'response-0221.json'),
                       response_sha256=hashlib.sha256((old/'response-0221.json').read_bytes()).hexdigest(),
                       probability_values_changed=False,new_network_request=False))
    client.append(dict(identity,event='validated',response=responses[221],validation_revision='JL-002-R1',
                       revalidated_saved_response=True,new_network_request=False,
                       listed_usage_cost_usd=str(Decimal(responses[221]['usage']['input_tokens'])*RATE_USD),
                       probability_mass_modes={'decision':probability_mass_policy(responses[221]['answers']['decision']['probabilities'])}))
    continuation=ContinueClient(client,cache,schedule)
    completed={(r['case_id'],r['arm']) for r in old_predictions}
    old_by_identity={(r['case_id'],r['arm']):r for r in old_predictions}
    stopped=None
    try:
        for i,case in enumerate(cases):
            order=checklists[(i//6+i)%6]
            for arm in arms[i%6]:
                if (case['id'],arm) in completed:
                    # Reconstruct every already-complete answer in memory; no network.
                    choice,history=run_arm(continuation,case,arm,order,prompts)
                    original=old_by_identity[case['id'],arm]
                    if choice!=original['choice'] or history!=original['history']:
                        raise Stop('saved completed prediction does not replay identically')
                    continue
                choice,history=run_arm(continuation,case,arm,order,prompts)
                row={'case_id':case['id'],'arm':arm,'choice':choice,'history':history,
                     'genuine':True,'input_sha256':hashlib.sha256(canonical(case['input'])).hexdigest(),
                     'checklist_order':order}
                with (OUT/'predictions.jsonl').open('ab') as f:
                    f.write(canonical(row)+b'\n');f.flush();os.fsync(f.fileno())
                completed.add((case['id'],arm))
            if i>=24:print(f'Completed case {i+1}/96; new API calls {client.calls-221}',flush=True)
    except Exception as exc:
        stopped=str(exc) if isinstance(exc,Stop) else type(exc).__name__
    events=[json.loads(x) for x in client.ledger.read_text().splitlines()]
    valid=[r for r in events if r['event']=='validated']
    summary={'live_mode':True,'genuine_jev_responses':True,'continuation_revision':'JL-002-R1',
             'parent_attempts':221,'new_attempts':client.calls-221,'attempts':client.calls,
             'validated_calls':len(valid),'completed_arm_predictions':len(completed),
             'stop':stopped,'historical_failure_preserved':True,'saved_response_revalidated':221,
             'parent_listed_cost_usd_including_rejected':str(parent_cost),
             'new_listed_cost_usd':str(client.actual_usd-parent_cost),'listed_cost_usd':str(client.actual_usd),
             'reserved_gbp':str(client.reserved),'hard_ceiling_gbp':'5','automatic_retries':0,
             'replayed_saved_calls':sorted(continuation.replayed)}
    (OUT/'execution.json').write_bytes(canonical(summary))
    (OUT/'prediction-seal.json').write_bytes(canonical({'sha256':hashlib.sha256((OUT/'predictions.jsonl').read_bytes()).hexdigest(),
                                                        'count':len(completed),'freeze_sha256':hashlib.sha256((ROOT/'freeze.json').read_bytes()).hexdigest()}))
    print(json.dumps({k:v for k,v in summary.items() if k!='replayed_saved_calls'},indent=2),flush=True)
    return summary


if __name__=='__main__':
    try:
        result=execute()
        if result['stop']:raise SystemExit(2)
    except Stop as exc:
        print(str(exc));raise SystemExit(2)
