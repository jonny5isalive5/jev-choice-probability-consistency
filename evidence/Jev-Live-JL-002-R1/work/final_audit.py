import hashlib,json,sys
from collections import Counter,defaultdict
from decimal import Decimal
from pathlib import Path

ROOT=Path('source/Jev-Live-JL-002-R1')
BASE=Path('evidence/Jev-Live-JL-002-R1')
sys.path.insert(0,str(ROOT))
from jev import canonical,validate,probability_mass_policy,RATE_USD,CALL_RESERVE
from pilot import verify_freeze

verify_freeze()
parent=Path('evidence/Jev-Live-JL-002/evidence/live-run-001')
run=BASE/'evidence/continued-run-001'
execution=json.loads((run/'execution.json').read_text())
score=json.loads((run/'score.json').read_text())
assert (run/'ledger.jsonl').read_bytes().startswith((parent/'ledger.jsonl').read_bytes())
assert (run/'predictions.jsonl').read_bytes().startswith((parent/'predictions.jsonl').read_bytes())
for i in range(1,222):assert (run/f'response-{i:04}.json').read_bytes()==(parent/f'response-{i:04}.json').read_bytes()
events=[json.loads(x) for x in (run/'ledger.jsonl').read_text().splitlines()]
reserved={r['sequence']:r for r in events if r['event']=='reserved'}
assert len(reserved)==sum(r['event']=='reserved' for r in events)
assert set(reserved)==set(range(1,execution['attempts']+1))
assert sorted(execution['replayed_saved_calls'])==list(range(2,222))
rounding=[];models=Counter();usage=defaultdict(lambda:Counter());top_keys=set()
for sequence,event in reserved.items():
    raw=(run/f'response-{sequence:04}.json').read_bytes()
    response=validate(json.loads(raw),event['request'])
    top_keys.update(response)
    models[response['model']]+=1
    p=response['answers']['decision']['probabilities']
    if probability_mass_policy(p)!='strict_unit_mass':
        rounding.append({'sequence':sequence,'probabilities':p,'sum':str(sum(Decimal(str(v)) for v in p.values()))})
    u=usage[event['arm']];u['calls']+=1
    u['input_tokens']+=response['usage']['input_tokens'];u['output_tokens']+=response['usage']['output_tokens']
total_input=sum(u['input_tokens'] for u in usage.values())
total_output=sum(u['output_tokens'] for u in usage.values())
cost=Decimal(total_input)*RATE_USD
assert cost==Decimal(execution['listed_cost_usd'])==Decimal(score['listed_total_usd'])
assert CALL_RESERVE*len(reserved)==Decimal(execution['reserved_gbp'])<=Decimal(5)
assert not score['audit_findings']
assert score['complete'] and execution['stop'] is None
assert execution['attempts']==865 and execution['new_attempts']==644
assert execution['completed_arm_predictions']==288
key=json.loads((ROOT/'answer_key.json').read_text())
predictions=[json.loads(x) for x in (run/'predictions.jsonl').read_text().splitlines()]
easy=[cid for cid,k in key.items() if k['variant']=='clean' and k['difficulty']=='easy_control']
controls={arm:{'correct':sum(p['choice']==key[p['case_id']]['expected'] for p in predictions if p['arm']==arm and p['case_id'] in easy),'total':len(easy)} for arm in ('single','swarm','sequential')}
confusion={arm:{truth:dict(Counter(p['choice'] for p in predictions if p['arm']==arm and key[p['case_id']]['expected']==truth)) for truth in ('ALLOW','DENY','ABSTAIN')} for arm in ('single','swarm','sequential')}
before=json.loads((BASE/'evidence/protected-before.json').read_text())
changed=[name for name,h in before.items() if not Path(name).is_file() or hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h]
assert not changed
protection={'checked_files':len(before),'changed':changed,'all_unchanged':True}
(BASE/'evidence/protected-after.json').write_text(json.dumps(protection,indent=2))
from secure_credential import credential
secret=credential().encode()
secret_hits=sum(secret in p.read_bytes() for base in (ROOT,BASE) for p in base.rglob('*') if p.is_file() and p.suffix!='.zip')
assert secret_hits==0
result={'source_freeze_verified':True,'source_freeze_sha256':hashlib.sha256((ROOT/'freeze.json').read_bytes()).hexdigest(),
        'original_ledger_preserved_as_exact_prefix':True,'original_predictions_preserved_as_exact_prefix':True,
        'original_221_response_files_byte_identical':True,'previous_calls_replayed_without_network':220,
        'new_calls':644,'combined_calls':865,'automatic_retries':0,
        'historical_stopped_events':[r for r in events if r['event']=='stopped'],
        'received_model_counts':dict(models),'response_top_level_fields':sorted(top_keys),
        'separate_server_fingerprint_present':'system_fingerprint' in top_keys,
        'rounding_compatible_responses':rounding,'rounding_compatible_count':len(rounding),
        'usage_by_arm':{arm:dict(u,listed_usd=str(Decimal(u['input_tokens'])*RATE_USD)) for arm,u in usage.items()},
        'total_input_tokens':total_input,'total_output_tokens':total_output,
        'total_listed_usd':str(cost),'prior_listed_usd':execution['parent_listed_cost_usd_including_rejected'],
        'new_listed_usd':execution['new_listed_cost_usd'],
        'gbp_estimate_using_prior_reference':str(cost*Decimal('0.7604301892533474')),
        'gbp_reference_is_not_settled_invoice':True,'max_context_reserved_gbp':execution['reserved_gbp'],
        'easy_clean_controls':controls,'confusion_all_96':confusion,
        'protected_files':protection,'plaintext_secret_occurrences':secret_hits}
(BASE/'evidence/continuation-audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
