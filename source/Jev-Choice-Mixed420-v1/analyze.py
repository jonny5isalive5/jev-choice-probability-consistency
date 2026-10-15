"""Independent descriptive analysis from raw response bytes. No collector import."""
import json,collections,hashlib
from pathlib import Path
from decimal import Decimal as D
ROOT=Path(r'evidence/Jev-Choice-Mixed420-Run-v1')
DESIGN=Path(r'evidence/Jev-Choice-Mixed420-Design-v1')
LABELS=('ALLOW','ABSTAIN','DENY')
def normalized(s): return s.replace('IGNORE','ABSTAIN')
def analyze(root=ROOT,design=DESIGN):
    pm=json.loads((design/'payload-manifest.json').read_text()); rows=[]; pairs=collections.defaultdict(dict); groups={}
    def add(key,row):
        g=groups.setdefault(key,{'usable':0,'mismatches':0,'mismatches_over_tolerance':0,'ties':0,'correct_controls':0,'choices':collections.Counter(),'probability_sums':{k:D(0) for k in LABELS},'confidence_sum':D(0)})
        g['usable']+=1; g['mismatches']+=row['gap']>0; g['mismatches_over_tolerance']+=row['gap']>D('.000001'); g['ties']+=row['tie']; g['correct_controls']+=row['control_correct'] is True
        g['choices'][row['normalized_choice']]+=1; g['confidence_sum']+=row['confidence']
        for k in LABELS:g['probability_sums'][k]+=row['normalized_probabilities'][k]
    for p in sorted((root/'live-run-001').glob('[0-9][0-9][0-9][0-9]')):
        m=json.loads((p/'attempt.json').read_text()); h=json.loads((p/'http.json').read_text()) if (p/'http.json').exists() else {}
        row={**m,'http_status':h.get('status'),'request_id':h.get('headers',{}).get('x-typesafe-request-id')}
        if (p/'observation.json').exists():
            raw=(p/'response.body').read_bytes(); r=json.loads(raw,parse_float=D); a=r['answers']['decision']; probs=a['probabilities']; peak=max(probs.values()); gap=peak-probs[a['choice']]
            expected=pm[m['payload']]['expected_control']; saved=json.loads((p/'observation.json').read_text())
            assert saved['choice']==a['choice'] and D(saved['gap'])==gap and saved['mismatch']==(gap>0)
            assert hashlib.sha256((p/'request.json').read_bytes()).hexdigest()==m['request_sha256']
            row.update(choice=a['choice'],normalized_choice=normalized(a['choice']),probabilities=probs,normalized_probabilities={normalized(k):D(v) for k,v in probs.items()},confidence=D(a['confidence']),gap=gap,mismatch=gap>0,mismatch_over_tolerance=gap>D('.000001'),tie=sum(v==peak for v in probs.values())>1,control_correct=None if expected is None else a['choice']==expected,model=r['model'],usage=r['usage'])
            for key in (m['arm'],m['module']+'/'+m['arm'],m['template']+'/'+m['arm'],'block-'+str(m['block'])+'/'+m['module']+'/'+m['arm'],'first-'+m['first_arm']+'/'+m['module']+'/'+m['arm']):add(key,row)
            pairs[m['pair_id']][m['arm']]=row
        else:row['failure']=json.loads((p/'failure.json').read_text()) if (p/'failure.json').exists() else 'unfinished'
        rows.append(row)
    paired=[]; pairgroups={}
    for pair_id,arms in sorted(pairs.items()):
        if set(arms)!={'ABSTAIN','IGNORE'}:continue
        a,i=arms['ABSTAIN'],arms['IGNORE']
        assert (a['template'],a['block'],a['first_arm'])==(i['template'],i['block'],i['first_arm'])
        deltas={k:i['normalized_probabilities'][k]-a['normalized_probabilities'][k] for k in LABELS}
        entry={'pair_id':pair_id,'block':a['block'],'module':a['module'],'template':a['template'],'first_arm':a['first_arm'],'abstain_choice':a['choice'],'ignore_raw_choice':i['choice'],'transition':a['normalized_choice']+' -> '+i['normalized_choice'],'changed_choice':a['normalized_choice']!=i['normalized_choice'],'probability_deltas_ignore_minus_abstain':deltas}
        paired.append(entry)
        for key in (a['module'],a['template'],'first-'+a['first_arm']+'/'+a['module'],'block-'+str(a['block'])+'/'+a['module']):
            g=pairgroups.setdefault(key,{'complete_pairs':0,'changed_choices':0,'transitions':collections.Counter(),'delta_sums':{k:D(0) for k in LABELS}})
            g['complete_pairs']+=1;g['changed_choices']+=entry['changed_choice'];g['transitions'][entry['transition']]+=1
            for k in LABELS:g['delta_sums'][k]+=deltas[k]
    for g in groups.values():
        g['mean_probabilities']={k:v/g['usable'] for k,v in g.pop('probability_sums').items()};g['mean_confidence']=g.pop('confidence_sum')/g['usable']
    for g in pairgroups.values():g['mean_probability_deltas_ignore_minus_abstain']={k:v/g['complete_pairs'] for k,v in g.pop('delta_sums').items()}
    inputs=sum(x.get('usage',{}).get('input_tokens',0) for x in rows); outputs=sum(x.get('usage',{}).get('output_tokens',0) for x in rows)
    return {'attempts':len(rows),'usable':sum('choice'in x for x in rows),'complete_pairs':len(paired),'incomplete_pairs':len({x['pair_id'] for x in rows})-len(paired),'request_ids_captured':sum(bool(x['request_id']) for x in rows),'input_tokens':inputs,'output_tokens':outputs,'estimated_usd':D(inputs)*D('.000000042'),'model_versions':sorted({x['model'] for x in rows if 'model'in x}),'groups':groups,'paired_groups':pairgroups,'mismatches':[x for x in rows if x.get('mismatch')],'rows':rows,'pairs':paired}
if __name__=='__main__':
    result=analyze()
    with (ROOT/'analysis.json').open('x') as f:json.dump(result,f,indent=2,default=str)
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','pairs','groups','paired_groups','mismatches')},default=str))
    print(json.dumps({k:result['groups'].get(k) for k in ('complex/ABSTAIN','complex/IGNORE','control/ABSTAIN','control/IGNORE')},default=str))
