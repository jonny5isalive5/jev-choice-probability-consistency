"""Offline, standard-library verification. No network, credentials, or live runners.

Run: python -B verify_publication.py
"""
from pathlib import Path
from decimal import Decimal as D
from collections import Counter
import json, hashlib, ast

ROOT=Path(__file__).resolve().parent
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()

RUNS=[
 ('JL001','Jev-Live-JL-001-live/live-run-001','response-*.json',0,217),
 ('JL002_original','Jev-Live-JL-002/evidence/live-run-001','response-*.json',0,221),
 ('JL002_R1_new','Jev-Live-JL-002-R1/evidence/continued-run-001','response-*.json',221,644),
 ('Repeat5_partial','Jev-Live-JL-002-Repeat5/evidence/live-batch/repeat-01','response-*.json',0,456),
 ('ABSTAIN240','Jev-Choice-Diagnostic-Run-v1/live-run-001','*/response.body',0,240),
 ('IGNORE240','Jev-Choice-IGNORE-Run-v1/live-run-001','*/response.body',0,240),
 ('Mixed420','Jev-Choice-Mixed420-Run-v1/live-run-001','*/response.body',0,420),
 ('Rounding100','Jev-Rounding100-Run-v1/live-run-001','*/response.body',0,100)]

def summarize():
 summary={};index=[]
 for name,folder,pattern,skip,expected in RUNS:
  counts=Counter();ins=outs=0
  for p in sorted((ROOT/'evidence'/folder).glob(pattern)):
   seq=int(p.stem.split('-')[-1]) if p.name.startswith('response-') else int(p.parent.name)
   if seq<=skip:continue
   raw=p.read_bytes();r=json.loads(raw,parse_float=D)
   assert r['model']=='jev-1.14.0'
   assert len(r['answers'])==1
   a=next(iter(r['answers'].values()));assert a['type']=='choice'
   probs={k:D(v) for k,v in a['probabilities'].items()};c=a['choice'];grid={k:v.quantize(D('.01')) for k,v in probs.items()}
   gap=max(probs.values())-probs[c];tails=[k for k,v in probs.items() if v!=grid[k]]
   counts['calls']+=1;counts['choice_max_mismatches']+=gap>D('.000001')
   counts['numeric_tail_responses']+=bool(tails);counts['nonselected_tails']+=any(k!=c for k in tails)
   counts['nonunit_grid_totals']+=sum(grid.values())!=1
   ins+=r['usage']['input_tokens'];outs+=r['usage']['output_tokens']
   index.append({'run':name,'sequence':seq,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(raw),'choice':c,'mismatch':gap>D('.000001')})
  assert counts['calls']==expected,(name,counts)
  summary[name]={**dict(counts),'input_tokens':ins,'output_tokens':outs,'listed_usd':str(D(ins)*D('.000000042'))}
 for seq in range(1,222):
  a=ROOT/'evidence'/RUNS[1][1]/f'response-{seq:04d}.json'
  b=ROOT/'evidence'/RUNS[2][1]/f'response-{seq:04d}.json'
  assert a.read_bytes()==b.read_bytes(),'Reused prefix differs'
 assert len(index)==2538
 assert sum(s['choice_max_mismatches'] for s in summary.values())==4
 assert sum(s['numeric_tail_responses'] for s in summary.values())==47
 assert sum(s['nonunit_grid_totals'] for s in summary.values())==5
 scores={}
 for label,folder,run in [('JL001','Jev-Live-JL-001-live','live-run-001'),('JL002_R1','Jev-Live-JL-002-R1','evidence/continued-run-001'),('Repeat5_partial','Jev-Live-JL-002-Repeat5','evidence/live-batch/repeat-01')]:
  key=read(f'source/{folder}/answer_key.json')
  rows=[json.loads(line) for line in (ROOT/f'evidence/{folder}/{run}/predictions.jsonl').read_text().splitlines()]
  counts={a:Counter() for a in ('single','swarm','sequential')}
  assert len({(r['case_id'],r['arm']) for r in rows})==len(rows)
  for r in rows:
   assert r['genuine'] is True
   k=key[r['case_id']];c=counts[r['arm']];c['completed']+=1;c['correct']+=r['choice']==k['expected']
   c['false_authorizations']+=r['choice']=='ALLOW' and k['expected']!='ALLOW'
   if k.get('variant')=='clean':c['clean_completed']+=1;c['clean_correct']+=r['choice']==k['expected']
  scores[label]={k:dict(v) for k,v in counts.items()}
 assert [scores['JL001'][a]['correct'] for a in ('single','swarm','sequential')]==[18,24,24]
 assert [scores['JL002_R1'][a]['correct'] for a in ('single','swarm','sequential')]==[48,45,43]
 assert [scores['JL002_R1'][a]['clean_correct'] for a in ('single','swarm','sequential')]==[33,30,29]
 rounding={'binary':Counter(),'ternary':Counter()}
 for p in (ROOT/'evidence'/RUNS[-1][1]).glob('*/response.body'):
  a=next(iter(json.loads(p.read_bytes(),parse_float=D)['answers'].values()));values=sorted((D(x).quantize(D('.01')) for x in a['probabilities'].values()),reverse=True)
  group=rounding['binary' if len(values)==2 else 'ternary'];group['calls']+=1;group['near_ties']+=values[0]-values[1]<=D('.01')
 assert rounding['binary']=={'calls':40,'near_ties':0} and rounding['ternary']=={'calls':60,'near_ties':13}
 total_in=sum(x['input_tokens'] for x in summary.values());total_out=sum(x['output_tokens'] for x in summary.values())
 return {'unique_live_calls':2538,'deduplicated_reused_R1_prefix':221,'runs':summary,'scores_recomputed_from_predictions':scores,'rounding_exposure':{k:dict(v) for k,v in rounding.items()},'total_input_tokens':total_in,'total_output_tokens':total_out,'total_usage_based_usd':str(D(total_in)*D('.000000042')),'invoice_verified':False},index

def verify():
 manifest=read('SHA256_MANIFEST.json')['files']
 actual={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256_MANIFEST.json' and '.git' not in p.relative_to(ROOT).parts}
 assert actual==manifest,'Publication manifest mismatch (missing, extra, or changed files)'
 for p in ROOT.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
 provenance=read('PUBLICATION_PROVENANCE.json')
 for entry in provenance['files']:
  assert sha((ROOT/entry['path']).read_bytes())==entry['publication_sha256']
 summary,index=summarize()
 assert summary==read('RESULTS_SUMMARY.json')
 assert index==read('LIVE_RESPONSE_INDEX.json')
 bypath={x['path']:x for x in provenance['files']}
 for row in index:
  assert bypath[row['path']]['modified'] is False,'Raw live response was modified'
  assert bypath[row['path']]['original_sha256']==row['sha256']
 # Exact recent request bytes remain as captured; old requests remain inside unchanged ledgers.
 for row in provenance['files']:
  if row['path'].startswith('evidence/') and ('/live-run-001/' in row['path'] or '/continued-run-001/' in row['path'] or '/repeat-01/' in row['path']):
   if row['path'].endswith('/request.json'):assert row['modified'] is False
 print(json.dumps({'status':'PASS','publication_files_verified':len(manifest),'unique_live_responses_verified':2538,'reused_responses_verified':221,'mismatches':4,'new_API_calls':0,'summary':summary},indent=2))

if __name__=='__main__':verify()
