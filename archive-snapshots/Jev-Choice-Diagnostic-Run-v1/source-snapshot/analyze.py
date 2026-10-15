"""Read-only independent extraction from response bodies; never imports collector."""
import json,hashlib,collections
from pathlib import Path
from decimal import Decimal as D
R=Path(r'evidence/Jev-Choice-Diagnostic-Run-v1')
def run():
    rows=[]; groups={}; bodies=collections.defaultdict(set); choices=collections.defaultdict(collections.Counter)
    for p in sorted((R/'live-run-001').glob('[0-9][0-9][0-9][0-9]')):
        meta=json.loads((p/'attempt.json').read_text()); http=json.loads((p/'http.json').read_text()) if (p/'http.json').exists() else {}
        row={**meta,'http_status':http.get('status'),'request_id':http.get('headers',{}).get('x-typesafe-request-id')}
        if (p/'observation.json').exists():
            raw=(p/'response.body').read_bytes(); r=json.loads(raw,parse_float=D); a=r['answers']['decision']; probs=a['probabilities']; top=max(probs.values()); gap=top-probs[a['choice']]
            saved=json.loads((p/'observation.json').read_text())
            assert saved['choice']==a['choice'] and D(saved['gap'])==gap and saved['mismatch']==(gap>0)
            assert hashlib.sha256((p/'request.json').read_bytes()).hexdigest()==meta['request_sha256']
            row.update(choice=a['choice'],probabilities=probs,confidence=a['confidence'],gap=gap,mismatch=gap>0,tie=sum(v==top for v in probs.values())>1,input_tokens=r['usage']['input_tokens'],output_tokens=r['usage']['output_tokens'],model=r['model'])
            expected=meta['payload'].removeprefix('control-').upper() if meta['module']=='control' else None
            row['control_correct']=None if expected is None else a['choice']==expected
            for key in ('all',meta['module'],'payload:'+meta['payload'],'block:'+str(meta['block'])):
                g=groups.setdefault(key,{'usable':0,'mismatches':0,'ties':0,'control_correct':0,'choices':collections.Counter()})
                g['usable']+=1; g['mismatches']+=gap>0; g['ties']+=row['tie']; g['control_correct']+=row['control_correct'] is True; g['choices'][a['choice']]+=1
            digest=meta['request_sha256']; bodies[digest].add(json.dumps(a,sort_keys=True,default=str)); choices[digest][a['choice']]+=1
        else: row['failure']=json.loads((p/'failure.json').read_text()) if (p/'failure.json').exists() else 'unfinished'
        rows.append(row)
    result={'attempts':len(rows),'groups':groups,'mismatches':[x for x in rows if x.get('mismatch')],
       'request_ids_captured':sum(bool(x['request_id']) for x in rows),'model_versions':sorted({x['model'] for x in rows if 'model'in x}),
       'input_tokens':sum(x.get('input_tokens',0) for x in rows),'output_tokens':sum(x.get('output_tokens',0) for x in rows),
       'estimated_usd':sum(x.get('input_tokens',0) for x in rows)*D('.000000042'),
       'by_identical_request':{k:{'distinct_answer_objects':len(bodies[k]),'choices':v} for k,v in choices.items()},'rows':rows}
    (R/'analysis.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','mismatches','by_identical_request')},default=str))
if __name__=='__main__': run()
