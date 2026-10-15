"""Frozen descriptive repeatability analysis; no live calls, no outcome selection."""
import itertools,json,statistics
from collections import Counter
from pathlib import Path
from score import score

ROOT=Path(__file__).parent
BASE=Path('evidence/Jev-Live-JL-002-Repeat5')
ARMS=('single','swarm','sequential')


def predictions(path):
    return {(r['case_id'],r['arm']):r for r in [json.loads(x) for x in (path/'predictions.jsonl').read_text().splitlines()]}


def aggregate(batch,original):
    baseline=json.loads((original/'score.json').read_text());base_predictions=predictions(original)
    repeats=[];all_predictions={}
    for i in range(1,6):
        path=batch/f'repeat-{i:02}'
        if not (path/'execution.json').exists():
            repeats.append({'repeat':i,'status':'NOT_STARTED_OR_UNSEALED'});continue
        result=score(path)
        (path/'score.json').write_text(json.dumps(result,indent=2))
        current=predictions(path);all_predictions[i]=current
        result['repeat']=i;result['status']='COMPLETE' if result['complete'] else 'PARTIAL'
        result['agreement_with_original']={arm:{'paired':sum(k[1]==arm and k in base_predictions for k in current),
            'same_final_choice':sum(k[1]==arm and k in base_predictions and p['choice']==base_predictions[k]['choice'] for k,p in current.items()),
            'same_full_final_answer':sum(k[1]==arm and k in base_predictions and p['history'][-1]['answer']==base_predictions[k]['history'][-1]['answer'] for k,p in current.items())} for arm in ARMS}
        repeats.append(result)
    complete=[r for r in repeats if r['status']=='COMPLETE']
    distribution={}
    for arm in ARMS:
        values=[r['arms'][arm]['clean_64']['correct'] for r in complete]
        distribution[arm]={'values':values,'minimum':min(values) if values else None,'maximum':max(values) if values else None,'mean':statistics.mean(values) if values else None}
    signs=Counter('swarm_ahead' if r['primary_clean_swarm_vs_sequential']['net_correct']>0 else 'tie' if r['primary_clean_swarm_vs_sequential']['net_correct']==0 else 'sequential_ahead' for r in complete)
    pairwise=[]
    for a,b in itertools.combinations(sorted(all_predictions),2):
        left,right=all_predictions[a],all_predictions[b]
        pairwise.append({'repeats':[a,b],'arms':{arm:{'paired':sum(k[1]==arm and k in right for k in left),
            'same_final_choice':sum(k[1]==arm and k in right and p['choice']==right[k]['choice'] for k,p in left.items())} for arm in ARMS}})
    unstable={arm:[] for arm in ARMS}
    if len(complete)==5:
        for k in all_predictions[1]:
            values=[all_predictions[i][k]['choice'] for i in range(1,6)]
            if len(set(values))>1:unstable[k[1]].append({'case_id':k[0],'choices_by_repeat':values})
    return {'original_reference':{k:v for k,v in baseline.items() if k!='failures'},
            'repeats':repeats,'complete_new_repeats':len(complete),'clean_accuracy_distribution':distribution,
            'primary_direction_counts':dict(signs),'predeclared_favorable_count':sum(r['predeclared_favorable_descriptive_signal'] for r in complete),
            'pairwise_agreement':pairwise,'cases_with_changing_final_choices':unstable,
            'independent_base_questions':64,'repeats_are_not_new_independent_questions':True,
            'general_superiority_or_significance_claim':False,'next_action':'STOP; retain all repeats and original reference separately'}


if __name__=='__main__':
    batch=BASE/'evidence/live-batch'
    original=Path('evidence/Jev-Live-JL-002-R1/evidence/continued-run-001')
    result=aggregate(batch,original)
    (BASE/'evidence/repeatability.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('original_reference','repeats','cases_with_changing_final_choices','pairwise_agreement')},indent=2))
