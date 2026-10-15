"""Five prospective serial repetitions, without inspecting scores during execution."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
from jev import Client,HTTPTransport,MockTransport,Stop,canonical,digest,MODEL
from pilot import verify_freeze,run_arm
from secure_credential import credential
from budget import SharedBudget,BudgetTransport,utc

ROOT=Path(__file__).parent
BASE=Path('evidence/Jev-Live-JL-002-Repeat5')


def check_parents():
    data=json.loads((ROOT/'repeat_protocol.json').read_text())
    for name,expected in data['parent_files'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected:raise Stop('frozen parent changed')
    return data


def run_one(index,directory,transport):
    verify_freeze()
    prompts=json.loads((ROOT/'prompts.json').read_text());cases=json.loads((ROOT/'cases.json').read_text())
    client=Client(transport,directory);predictions=directory/'predictions.jsonl'
    predictions.touch(exist_ok=False)
    started=utc();stopped=None;complete=0;smoke_ok=False
    try:
        smoke_request={'model':MODEL,'state':'The light is green. Authorize exactly when the light is green.',
                       'questions':{'decision':{'type':'choice','instructions':'Select ALLOW if authorization is established, DENY if ruled out, ABSTAIN if unresolved.',
                                               'criteria':prompts['options']}}}
        smoke=client.call(smoke_request,'SMOKE','smoke',0)
        if transport.genuine and smoke['decision']['choice']!='ALLOW':raise Stop('known smoke failed; evaluation not started')
        smoke_ok=True
        orders=list(itertools.permutations(('single','swarm','sequential')))
        perspectives=list(itertools.permutations(range(3)))
        for i,case in enumerate(cases):
            order=perspectives[(i//6+i)%6]
            for arm in orders[i%6]:
                choice,history=run_arm(client,case,arm,order,prompts)
                row={'case_id':case['id'],'arm':arm,'choice':choice,'history':history,
                     'genuine':transport.genuine,'input_sha256':digest(case['input']),'checklist_order':order}
                with predictions.open('ab') as f:f.write(canonical(row)+b'\n');f.flush();os.fsync(f.fileno())
                complete+=1
            if (i+1)%8==0:print(f'Repeat {index}/5: {i+1}/96 cases complete',flush=True)
    except Exception as exc:
        stopped=str(exc) if isinstance(exc,Stop) else type(exc).__name__
    ledger=[json.loads(x) for x in client.ledger.read_text().splitlines()]
    validated=[r for r in ledger if r['event']=='validated']
    summary={'repeat':index,'live_mode':transport.genuine,'genuine_jev_responses':transport.genuine and bool(validated),
             'requested_model':MODEL,'returned_models':sorted({r['response']['model'] for r in validated}),
             'started_utc':started,'finished_utc':utc(),'attempts':client.calls,'validated_calls':len(validated),
             'completed_arm_predictions':complete,'smoke_passed':smoke_ok,'stop':stopped,
             'listed_cost_usd':str(client.actual_usd),'reserved_gbp':str(client.reserved),
             'reservation_note':'Local full-context accounting only. Shared settled budget is authoritative across repetitions.',
             'automatic_retries':0}
    (directory/'execution.json').write_bytes(canonical(summary))
    (directory/'prediction-seal.json').write_bytes(canonical({'sha256':hashlib.sha256(predictions.read_bytes()).hexdigest(),
        'count':complete,'freeze_sha256':hashlib.sha256((ROOT/'freeze.json').read_bytes()).hexdigest()}))
    return summary


def execute(live):
    verify_freeze();protocol=check_parents()
    if live:
        ready=json.loads((BASE/'evidence/readiness.json').read_text())
        if not ready.get('authenticated_models_access'):raise Stop('authenticated readiness missing')
        secret=credential()
        if not secret:raise Stop('authorized named credential missing')
    batch=BASE/'evidence'/('live-batch' if live else 'mock-batch')
    batch.mkdir(exist_ok=False) # never silently rerun or resume a campaign
    budget=SharedBudget(batch/'budget.jsonl',protocol['historical_listed_usd'])
    results=[];stopped=None
    try:
        for index in range(1,6):
            verify_freeze();check_parents()
            inner=HTTPTransport(secret) if live else MockTransport()
            result=run_one(index,batch/f'repeat-{index:02}',BudgetTransport(inner,budget,index))
            results.append(result)
            if result['stop']:
                stopped=f"Repeat {index}: {result['stop']}";break
            print(f'Repeat {index}/5 complete; no scoring or adaptation between repeats.',flush=True)
    except Exception as exc:
        stopped=str(exc) if isinstance(exc,Stop) else type(exc).__name__
    summary={'live_mode':live,'planned_repeats':5,'finished_repeats':len(results),
             'complete_repeats':sum(r['completed_arm_predictions']==288 and r['stop'] is None for r in results),
             'stop':stopped,'results':results,'budget':budget.snapshot(),'finished_utc':utc()}
    (batch/'batch.json').write_bytes(canonical(summary))
    print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2),flush=True)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');args=parser.parse_args()
    try:
        result=execute(args.live)
        if result['stop']:raise SystemExit(2)
    except Stop as exc:print(str(exc));raise SystemExit(2)
