import json,collections,hashlib
from pathlib import Path
from decimal import Decimal as D
from hypothesis import classify
ROOT=Path(r'evidence/Jev-Rounding100-Run-v1')
def analyze(root=ROOT):
    rows=[];groups={}
    for p in sorted((root/'live-run-001').glob('[0-9][0-9][0-9][0-9]')):
        m=json.loads((p/'attempt.json').read_text());h=json.loads((p/'http.json').read_text()) if (p/'http.json').exists() else {}
        row={**m,'http_status':h.get('status'),'request_id':h.get('headers',{}).get('x-typesafe-request-id')}
        if (p/'observation.json').exists():
            raw=(p/'response.body').read_bytes();r=json.loads(raw,parse_float=D);a=r['answers']['decision'];probs={k:D(v) for k,v in a['probabilities'].items()};peak=max(probs.values());gap=peak-probs[a['choice']]
            saved=json.loads((p/'observation.json').read_text());assert saved['choice']==a['choice'] and D(saved['gap'])==gap and saved['mismatch']==(gap>0)
            assert hashlib.sha256((p/'request.json').read_bytes()).hexdigest()==m['request_sha256']
            fit=classify(probs,a['choice']);ordered=sorted(fit['reported_grid'].values(),reverse=True);near=ordered[0]-ordered[1]<=D('.01');spread=ordered[0]-ordered[-1]
            row.update(choice=a['choice'],probabilities=probs,confidence=a['confidence'],gap=gap,mismatch=gap>D('1e-12'),original_tolerance_mismatch=gap>D('.000001'),tie=sum(v==peak for v in probs.values())>1,near_tie=near,reported_spread=spread,model=r['model'],usage=r['usage'],hypothesis=fit)
            for key in (m['arm'],m['payload'],'block-'+str(m['block'])+'/'+m['arm']):
                g=groups.setdefault(key,{'usable':0,'near_ties':0,'mismatches':0,'ties':0,'choices':collections.Counter(),'residual':collections.Counter(),'plain':collections.Counter(),'nonzero_required':0,'tail_responses':0,'nonselected_tails':0,'nonunit_totals':0,'all_options_spread_le_002':0})
                g['usable']+=1;g['near_ties']+=near;g['mismatches']+=row['mismatch'];g['ties']+=row['tie'];g['choices'][a['choice']]+=1;g['residual'][fit['residual_status']]+=1;g['plain'][fit['plain']['status']]+=1;g['nonzero_required']+=fit['nonzero_correction_required'];g['tail_responses']+=bool(fit['raw_tail_labels']);g['nonselected_tails']+=any(k!=a['choice'] for k in fit['raw_tail_labels']);g['nonunit_totals']+=abs(sum(probs.values())-1)>D('1e-12');g['all_options_spread_le_002']+=spread<=D('.02')
        else:row['failure']=json.loads((p/'failure.json').read_text()) if (p/'failure.json').exists() else 'unfinished'
        rows.append(row)
    binary=groups.get('binary',{});ternary=groups.get('ternary',{});adequate=binary.get('near_ties',0)>=10 and ternary.get('near_ties',0)>=15
    contradictions=[x for x in rows if x.get('hypothesis',{}).get('residual_status')=='incompatible'];boundaries=[x for x in rows if x.get('hypothesis',{}).get('residual_status')=='boundary_ambiguous']
    verdict='specified_residual_algorithm_contradicted' if contradictions else 'boundary_ambiguity_unresolved' if boundaries else 'compatible_in_bounded_near_tie_challenge_not_confirmed' if adequate else 'insufficient_near_tie_exposure'
    inp=sum(x.get('usage',{}).get('input_tokens',0) for x in rows)
    return {'attempts':len(rows),'usable':sum('choice'in x for x in rows),'ids_captured':sum(bool(x['request_id']) for x in rows),'input_tokens':inp,'output_tokens':sum(x.get('usage',{}).get('output_tokens',0) for x in rows),'cost_usd':D(inp)*D('.000000042'),'adequate_exposure':adequate,'verdict':verdict,'groups':groups,'contradictions':contradictions,'mismatches':[x for x in rows if x.get('mismatch')],'rows':rows}
if __name__=='__main__':
    a=analyze()
    with (ROOT/'analysis.json').open('x') as f:json.dump(a,f,indent=2,default=str)
    print(json.dumps({k:v for k,v in a.items() if k not in ('rows','contradictions','mismatches','groups')},default=str))
    print(json.dumps({k:a['groups'].get(k) for k in ('binary','ternary')},default=str))
