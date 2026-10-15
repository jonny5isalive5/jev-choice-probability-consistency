"""Read-only integrity, accounting and descriptive wire-variation checks."""
import hashlib,json,sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT=Path('source/Jev-Live-JL-002-Repeat5')
BASE=Path('evidence/Jev-Live-JL-002-Repeat5')
sys.path.insert(0,str(ROOT))
from jev import validate,strict_json,canonical,probability_mass_policy,RATE_USD,CALL_RESERVE
from pilot import verify_freeze
from repeat import check_parents
verify_freeze();protocol=check_parents()
batch=BASE/'evidence/live-batch';execution=json.loads((batch/'batch.json').read_text())
analysis=json.loads((BASE/'evidence/repeatability.json').read_text())
original=Path('evidence/Jev-Live-JL-002-R1/evidence/continued-run-001')

def lines(path):return [json.loads(x) for x in path.read_text().splitlines()]
old_events=lines(original/'ledger.jsonl')
old_requests={r['sequence']:r['request'] for r in old_events if r['event']=='reserved'}
old_responses={r['sequence']:r['response'] for r in old_events if r['event']=='validated'}
new_input=0;new_output=0;received_input=0;received_output=0;attempts=0;models=Counter();reports=[];budget_expected=[]
for i in range(1,6):
    run=batch/f'repeat-{i:02}'
    if not (run/'execution.json').exists():
        reports.append({'repeat':i,'status':'NOT_STARTED_OR_UNSEALED'});continue
    events=lines(run/'ledger.jsonl');summary=json.loads((run/'execution.json').read_text())
    reservations=[e for e in events if e['event']=='reserved']
    received={e['sequence']:e for e in events if e['event']=='received'}
    validated={e['sequence']:e for e in events if e['event']=='validated'}
    assert [e['sequence'] for e in reservations]==list(range(1,len(reservations)+1))
    same_payload=changed_answers=changed_choice=0;max_drift=Decimal(0)
    rounded=[];rep_input=rep_output=rep_received_input=rep_received_output=0;failures=[e for e in events if e['event']=='stopped']
    rejected=[]
    for event in reservations:
        seq=event['sequence'];attempts+=1
        assert event['genuine'] is True
        assert hashlib.sha256(canonical(event['request'])).hexdigest()==event['request_sha256']
        expected={'repeat':i,'local_sequence':seq,'validated_usage':None}
        if seq in received:
            raw=(run/f'response-{seq:04}.json').read_bytes()
            assert hashlib.sha256(raw).hexdigest()==received[seq]['response_sha256']
            parsed=strict_json(raw);u=parsed.get('usage',{})
            assert all(type(u.get(k)) is int and u[k]>=0 for k in ('input_tokens','output_tokens'))
            rep_received_input+=u['input_tokens'];rep_received_output+=u['output_tokens']
            if seq not in validated:
                rejected.append({'sequence':seq,'case_id':event['case_id'],'arm':event['arm'],'response':parsed,
                    'reported_usage_cost_usd':str(Decimal(u['input_tokens'])*RATE_USD),
                    'same_request_as_original':event['request']==old_requests[seq],
                    'original_response':old_responses[seq]})
            if seq in validated:
                response=validate(strict_json(raw),event['request'])
                assert response==validated[seq]['response']
                models[response['model']]+=1
                u=response['usage'];rep_input+=u['input_tokens'];rep_output+=u['output_tokens']
                expected['validated_usage']=u['input_tokens']
                a=response['answers']['decision'];p=a['probabilities']
                if probability_mass_policy(p)!='strict_unit_mass':rounded.append(seq)
                if event['request']==old_requests[seq]:
                    same_payload+=1;old=old_responses[seq]['answers']['decision']
                    changed_answers+=a!=old;changed_choice+=a['choice']!=old['choice']
                    max_drift=max(max_drift,max(abs(Decimal(str(p[k]))-Decimal(str(old['probabilities'][k]))) for k in p))
        budget_expected.append(expected)
    new_input+=rep_input;new_output+=rep_output;received_input+=rep_received_input;received_output+=rep_received_output
    assert Decimal(summary['listed_cost_usd'])==Decimal(rep_input)*RATE_USD
    score=json.loads((run/'score.json').read_text())
    assert not score['audit_findings']
    rows=lines(run/'predictions.jsonl');old_rows={(r['case_id'],r['arm']):r for r in lines(original/'predictions.jsonl')}
    current={(r['case_id'],r['arm']):r for r in rows}
    common=sorted({k[0] for k in current if all((k[0],arm) in current for arm in ('single','swarm','sequential'))})
    key=json.loads((ROOT/'answer_key.json').read_text())
    paired={}
    for arm in ('single','swarm','sequential'):
        paired[arm]={'cases':len(common),'repeat_correct':sum(current[cid,arm]['choice']==key[cid]['expected'] for cid in common),
            'original_correct_same_cases':sum(old_rows[cid,arm]['choice']==key[cid]['expected'] for cid in common),
            'changed_final_choices':sum(current[cid,arm]['choice']!=old_rows[cid,arm]['choice'] for cid in common)}
    reports.append({'repeat':i,'status':'COMPLETE' if score['complete'] else 'PARTIAL','attempts':len(reservations),
        'input_tokens':rep_input,'output_tokens':rep_output,'listed_usd':str(Decimal(rep_input)*RATE_USD),
        'all_received_input_tokens':rep_received_input,'all_received_output_tokens':rep_received_output,
        'all_received_listed_usd':str(Decimal(rep_received_input)*RATE_USD),'rejected_responses':rejected,
        'common_complete_case_ids':common,'paired_original_repeat_on_common_cases':paired,
        'historical_reference_payloads_identical':same_payload,'different_answers_on_identical_payloads':changed_answers,
        'different_choices_on_identical_payloads':changed_choice,'maximum_probability_change_on_identical_payload':str(max_drift),
        'rounded_mass_sequences':rounded,'failures':failures,'started_utc':summary['started_utc'],'finished_utc':summary['finished_utc']})

budget_events=lines(batch/'budget.jsonl');balance=Decimal(protocol['historical_listed_usd'])*2
peak=balance;sequence=0;pending=False;new_usd=Decimal(0)
for event in budget_events:
    kind=event['event']
    if kind=='reserved':
        assert not pending
        sequence+=1;assert event['global_sequence']==sequence
        assert event['repeat']==budget_expected[sequence-1]['repeat']
        balance+=CALL_RESERVE;pending=True
    elif kind=='settled':
        assert pending and event['global_sequence']==sequence
        expected=budget_expected[sequence-1]
        assert event['input_tokens']==expected['validated_usage']
        usd=Decimal(event['input_tokens'])*RATE_USD
        assert Decimal(event['listed_usd'])==usd
        balance+=usd*2-CALL_RESERVE;new_usd+=usd;pending=False
    elif kind=='unresolved_retained':assert pending
    elif kind!='opened':raise AssertionError('unknown budget event')
    assert Decimal(event['accounted_gbp'])==balance
    assert balance<=Decimal(5)
    peak=max(peak,balance)
assert sequence==execution['budget']['new_attempts']
assert new_usd==Decimal(execution['budget']['new_listed_usd'])==Decimal(new_input)*RATE_USD
assert balance==Decimal(execution['budget']['accounted_gbp_at_conservative_rate'])
before=json.loads((BASE/'evidence/protected-before.json').read_text())
changed=[name for name,h in before.items() if not Path(name).is_file() or hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h]
assert not changed
from secure_credential import credential
secret=credential().encode()
hits=sum(secret in p.read_bytes() for folder in (ROOT,BASE) for p in folder.rglob('*') if p.is_file() and p.suffix!='.zip')
assert hits==0
result={'source_freeze_verified':True,'parent_hashes_verified':True,'original_files_checked':len(before),'original_files_changed':changed,
        'new_inference_attempts':attempts,'new_validated_input_tokens':new_input,'new_validated_output_tokens':new_output,
        'new_all_received_input_tokens':received_input,'new_all_received_output_tokens':received_output,
        'new_all_received_listed_usd':str(Decimal(received_input)*RATE_USD),
        'new_all_received_gbp_estimate_prior_reference':str(Decimal(received_input)*RATE_USD*Decimal('0.7604301892533474')),
        'combined_all_received_listed_usd_including_history':str(Decimal(protocol['historical_listed_usd'])+Decimal(received_input)*RATE_USD),
        'reported_models':dict(models),'automatic_retries':0,'new_listed_usd':str(new_usd),
        'new_gbp_estimate_prior_reference':str(new_usd*Decimal('0.7604301892533474')),
        'historical_listed_usd_in_guard':protocol['historical_listed_usd'],'combined_usd_in_guard':execution['budget']['combined_listed_usd'],
        'maximum_accounted_gbp_including_inflight_reservations':str(peak),'final_accounted_gbp_including_prior_runs':str(balance),
        'shared_cap_gbp':'5','plaintext_secret_occurrences':hits,'repeats':reports,
        'completed_new_repeats':analysis['complete_new_repeats'],'stopped':execution['stop'],
        'model_fingerprint_note':'Pinned returned model string only; separate server fingerprint unavailable; no client seed or cache control.'}
(BASE/'evidence/final-audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
