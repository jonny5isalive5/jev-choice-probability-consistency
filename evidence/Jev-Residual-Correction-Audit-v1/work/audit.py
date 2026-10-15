import json,hashlib,collections,itertools
from pathlib import Path
from decimal import Decimal as D, ROUND_HALF_UP
ROOT=Path(r'evidence/Jev-Residual-Correction-Audit-v1')
CENT=D('.01'); EPS=D('1e-12')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[
 ('JL001',Path(r'evidence/Jev-Live-JL-001-live\live-run-001'),'response-*.json',0),
 ('JL002_original',Path(r'evidence/Jev-Live-JL-002\evidence\live-run-001'),'response-*.json',0),
 ('JL002_R1_new',Path(r'evidence/Jev-Live-JL-002-R1\evidence\continued-run-001'),'response-*.json',221),
 ('Repeat5_partial',Path(r'evidence/Jev-Live-JL-002-Repeat5\evidence\live-batch\repeat-01'),'response-*.json',0),
 ('ABSTAIN240',Path(r'evidence/Jev-Choice-Diagnostic-Run-v1\live-run-001'),'*/response.body',0),
 ('IGNORE240',Path(r'evidence/Jev-Choice-IGNORE-Run-v1\live-run-001'),'*/response.body',0),
 ('Mixed420',Path(r'evidence/Jev-Choice-Mixed420-Run-v1\live-run-001'),'*/response.body',0)]
original=sources[1][1];continued=sources[2][1]
for i in range(1,222):assert (original/f'response-{i:04d}.json').read_bytes()==(continued/f'response-{i:04d}.json').read_bytes()
rows=[];stats={};models=collections.Counter()
for name,root,pattern,skip in sources:
 st=collections.Counter()
 for p in sorted(root.glob(pattern)):
  number=int(p.stem.split('-')[-1]) if p.name.startswith('response-') else int(p.parent.name)
  if number<=skip:continue
  raw=p.read_bytes();r=json.loads(raw,parse_float=D);models[r['model']]+=1;st['responses']+=1
  for q,a in r['answers'].items():
   if a.get('type')!='choice':st['non_choice_answers']+=1;continue
   probs={k:D(v) for k,v in a['probabilities'].items()};c=a['choice'];rounded={k:v.quantize(CENT) for k,v in probs.items()};sort=sorted(rounded.values(),reverse=True)
   tails=[k for k,v in probs.items() if v!=rounded[k]];offgrid=[k for k,v in probs.items() if abs(v-rounded[k])>EPS]
   total=sum(rounded.values());gap=max(probs.values())-probs[c];margin=sort[0]-sort[1];n=len(probs);conf=D(a['confidence']);formula=(max(probs.values())-D(1)/n)/(D(1)-D(1)/n)
   grid_formula=(max(rounded.values())-D(1)/n)/(D(1)-D(1)/n)
   candidates=[]
   if abs(sum(probs.values())-1)<=EPS and not offgrid:
    for adjustment in (-CENT,D(0),CENT):
     qgrid=dict(rounded);qgrid[c]-=adjustment
     if not all(0<=v<=1 for v in qgrid.values()):continue
     if adjustment!=1-sum(qgrid.values()) or qgrid[c]<max(qgrid.values()):continue
     reconstructed=dict(qgrid);reconstructed[c]+=adjustment
     if reconstructed!=rounded:continue
     candidates.append({'pre_correction_grid':qgrid,'adjustment_to_choice':adjustment})
   tail_matches=[]
   for k in tails:
    target=float(probs[k]);matches=[]
    for cent in range(101):
     for sign in (-1,1):
      if float(D(cent)/100)+sign*.01==target:matches.append({'pre_cent':str(D(cent)/100),'delta':sign*.01})
    tail_matches.append({'label':k,'matches':matches})
   st['choice_answers']+=1;st['numeric_tail_responses']+=bool(tails);st['tails_on_nonchosen']+=any(k!=c for k in tails);st['mass_099_or_101']+=total in (D('.99'),D('1.01'));st['not_unit_mass_grid']+=total!=1;st['mismatches']+=gap>EPS;st['gap_above_cent']+=gap>CENT+EPS;st['near_ties_grid_001']+=margin<=CENT;st['max_ties_grid']+=margin==0;st['confidence_not_exact_formula']+=abs(conf-formula)>EPS;st['confidence_outside_halfcent']+=abs(conf-grid_formula)>D('.005')+EPS;st['no_grid_inverse_candidate']+=not candidates
   rows.append({'run':name,'sequence':number,'path':str(p),'sha256':sha(p),'question':q,'model':r['model'],'choice':c,'probabilities':probs,'rounded_grid':rounded,'grid_total':total,'confidence':conf,'confidence_formula':formula,'gap':gap,'top_two_margin_on_grid':margin,'tail_labels':tails,'offgrid_over_tolerance':offgrid,'tail_float_arithmetic_matches':tail_matches,'inverse_grid_candidates':candidates})
 stats[name]=dict(st)
# Independently resolve the one complex case; no imports from frozen evaluators.
req=json.loads(Path(r'evidence/Jev-Choice-Diagnostic-Design-v1\payloads\original.json').read_bytes());e=req['state']['original_evidence'];target=e['request'];rank=e['record_rules']['authority_rank'];facts={};selected={}
for fact in e['base_facts']:
 applicable=[x for x in e['records'] if x['fact']==fact and x['asset']==target['asset'] and x['revision']==target['revision'] and x['issued_at']<=target['as_of']<=x['valid_until'] and x['source'] in rank]
 if not applicable:facts[fact]=None;selected[fact]=[];continue
 best=max((rank[x['source']],x['issued_at']) for x in applicable)
 winners=[x for x in applicable if (rank[x['source']],x['issued_at'])==best];values={x['value'] for x in winners};facts[fact]=next(iter(values)) if len(values)==1 else None;selected[fact]=winners
unknown=[k for k,v in facts.items() if v is None];completions=[]
for vals in itertools.product((False,True),repeat=len(unknown)):
 f={**facts,**dict(zip(unknown,vals))};eligible=f['owner_consent'] and f['identity_verified'] and (f['training_current'] or f['supervision_available']) and f['inspection_passed'] and (f['permit_valid'] or f['waiver_valid']) and not f['hold_active'];completions.append({'unknown_assignment':dict(zip(unknown,vals)),'eligible':eligible})
assert unknown==['waiver_valid'] and all(x['eligible'] for x in completions)
# Constructive counterexample to the proposed spinner refutation criterion.
latent={'A':D('.3351'),'B':D('.3352'),'C':D('.3297')};assert sum(latent.values())==1
chosen=max(latent,key=latent.get);q={k:v.quantize(CENT,rounding=ROUND_HALF_UP) for k,v in latent.items()};delta=1-sum(q.values());reported=dict(q);reported[chosen]+=delta
assert chosen=='B' and reported=={'A':D('.34'),'B':D('.33'),'C':D('.33')}
result={'scope':'all identified genuine saved calls; reused 221 R1 responses excluded after byte verification; synthetic JS and mock runs excluded','unique_live_responses':sum(x['responses'] for x in stats.values()),'model_counts':models,'stats':stats,'rows':rows,'gold_case':{'facts':facts,'unknown':unknown,'completions':completions,'answer':'ALLOW','status':'post hoc standalone analysis; no frozen score edited'},'spinner_counterexample':{'unrounded':latent,'selected':chosen,'rounded_before':q,'adjustment':delta,'reported':reported,'conclusion':'0.34/0.33/0.33 with the 0.34 option not selected can occur under the proposed correction mechanism; it is not a valid standalone refutation'}}
(ROOT/'audit.json').write_text(json.dumps(result,indent=2,default=str))
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2,default=str))
