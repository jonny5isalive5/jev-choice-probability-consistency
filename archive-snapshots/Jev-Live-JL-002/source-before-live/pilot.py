"""JL-002 execution. Reads frozen inputs/prompts only, never imports or loads truth."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
from jev import Client,HTTPTransport,MockTransport,MODEL,Stop,canonical,digest
from secure_credential import credential

ROOT=Path(__file__).parent


def verify_freeze():
    manifest=json.loads((ROOT/'freeze.json').read_text())
    current={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.iterdir()
             if p.is_file() and p.name!='freeze.json'}
    if current!=manifest['files']:raise Stop('source, inputs, prompts or scorer differ from freeze')


def make_request(evidence,instruction,history,prompts):
    return {'model':MODEL,'state':{'original_evidence':evidence,'prior_judgments':history},
            'questions':{'decision':{'type':'choice','instructions':prompts['base']+instruction,
                                     'criteria':prompts['options']}}}


def run_arm(client,case,arm,checklist_order,prompts):
    evidence=case['input'];history=[]
    if arm=='single':
        instruction=prompts['single']+' '+' '.join(prompts['checklists'])
        answer=client.call(make_request(evidence,instruction,[],prompts),case['id'],arm,0)['decision']
        return answer['choice'],[{'instruction':instruction,'answer':answer}]
    if arm not in ('swarm','sequential'):raise Stop('unknown arm')
    for stage in range(4):
        instruction=prompts['checklists'][checklist_order[stage]] if stage<3 else prompts['synthesis']
        visible=history if arm=='sequential' or stage==3 else []
        answer=client.call(make_request(evidence,instruction,visible,prompts),case['id'],arm,stage)['decision']
        history.append({'instruction':instruction,'answer':answer})
    return history[-1]['answer']['choice'],history


def execute(live):
    verify_freeze()
    protocol=json.loads((ROOT/'protocol.json').read_text())
    prompts=json.loads((ROOT/'prompts.json').read_text())
    cases=json.loads((ROOT/'cases.json').read_text())
    if len(cases)!=96:raise Stop('case count changed')
    out=Path(protocol['evidence_root'])/('live-run-001' if live else 'mock-run-001')
    if live:
        readiness=json.loads((Path(protocol['evidence_root'])/'readiness.json').read_text())
        if not readiness.get('authenticated_models_access'):raise Stop('authenticated readiness not established')
        secret=credential()
        if not secret:raise Stop('authorized named credential missing')
        transport=HTTPTransport(secret)
    else:transport=MockTransport()
    client=Client(transport,out)
    predictions=out/'predictions.jsonl'
    predictions.touch(exist_ok=False)
    stopped=None;smoke_ok=False;complete=0
    try:
        smoke_request={'model':MODEL,'state':'The light is green. Authorize exactly when the light is green.',
                       'questions':{'decision':{'type':'choice','instructions':'Select ALLOW if authorization is established, DENY if ruled out, ABSTAIN if unresolved.',
                                               'criteria':prompts['options']}}}
        smoke=client.call(smoke_request,'SMOKE','smoke',0)
        if live and smoke['decision']['choice']!='ALLOW':raise Stop('known smoke failed; evaluation not started')
        smoke_ok=True
        print('Smoke passed. Starting frozen 96-case evaluation.',flush=True)
        orders=list(itertools.permutations(('single','swarm','sequential')))
        perspectives=list(itertools.permutations(range(3)))
        for i,case in enumerate(cases):
            checklist_order=perspectives[(i//6+i)%6]
            for arm in orders[i%6]:
                choice,history=run_arm(client,case,arm,checklist_order,prompts)
                row={'case_id':case['id'],'arm':arm,'choice':choice,'history':history,
                     'genuine':live,'input_sha256':digest(case['input']),'checklist_order':checklist_order}
                with predictions.open('ab') as f:
                    f.write(canonical(row)+b'\n');f.flush();os.fsync(f.fileno())
                complete+=1
            print(f'Completed case {i+1}/96',flush=True)
    except Exception as exc:
        stopped=str(exc) if isinstance(exc,Stop) else type(exc).__name__
    ledger=[json.loads(x) for x in client.ledger.read_text().splitlines()]
    validated=[r for r in ledger if r['event']=='validated']
    summary={'live_mode':live,'genuine_jev_responses':live and bool(validated),
             'requested_model':MODEL,'returned_models':sorted({r['response']['model'] for r in validated}),
             'attempts':client.calls,'validated_calls':len(validated),'completed_arm_predictions':complete,
             'smoke_passed':smoke_ok,'stop':stopped,'listed_cost_usd':str(client.actual_usd) if live else '0',
             'reserved_gbp':str(client.reserved),'hard_ceiling_gbp':'5','automatic_retries':0}
    (out/'execution.json').write_bytes(canonical(summary))
    (out/'prediction-seal.json').write_bytes(canonical({'sha256':hashlib.sha256(predictions.read_bytes()).hexdigest(),
                                                       'count':complete,'freeze_sha256':hashlib.sha256((ROOT/'freeze.json').read_bytes()).hexdigest()}))
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');args=parser.parse_args()
    try:
        result=execute(args.live)
        if result['stop']:raise SystemExit(2)
    except Stop as exc:
        print(str(exc));raise SystemExit(2)
