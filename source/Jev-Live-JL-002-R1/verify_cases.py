"""Independent checker: parse visible policy text; resolve visible records; enumerate worlds.
Does not import the authoring module or use private_rules/resolved_possibilities.
"""
import itertools
import json
import re
from collections import Counter
from pathlib import Path


def parse(text):
    name, description = text.removesuffix('.').split(' is true exactly when ')
    operands = re.search(r'\[([^]]+)\]',description).group(1).split(', ')
    if description.endswith(' is false'):
        return name, 'negate', operands, None
    if description.startswith('all of '): return name,'conjunction',operands,None
    if description.startswith('any of '): return name,'disjunction',operands,None
    match=re.match(r'(at least|exactly) (\d+) of ',description)
    if not match: raise ValueError('unrecognized policy text')
    return name,match[1],operands,int(match[2])


def solve(state):
    q=state['request']; ranks=state['record_rules']['authority_rank']
    choices={}
    for name in state['base_facts']:
        candidates=[]
        for record in state['records']:
            if record['fact']!=name:continue
            if record['asset']!=q['asset'] or record['revision']!=q['revision']:continue
            if record['source'] not in ranks:continue
            if record['issued_at']>q['as_of'] or record['valid_until']<q['as_of']:continue
            candidates.append(record)
        candidates.sort(key=lambda x:(ranks[x['source']],x['issued_at']),reverse=True)
        claims=set()
        if candidates:
            first=candidates[0]
            for r in candidates:
                if (ranks[r['source']],r['issued_at'])==(ranks[first['source']],first['issued_at']):
                    claims.add(r['value'])
        choices[name]=list(claims) if len(claims)==1 else [False,True]
    rules=[parse(s) for s in state['policy_rules']]
    outcomes=set()
    for assignment in itertools.product(*choices.values()):
        values=dict(zip(choices,assignment));pending=list(rules)
        while pending:
            progressed=False
            for rule in list(pending):
                name,operator,args,threshold=rule
                if any(a not in values for a in args):continue
                tally=sum(1 for a in args if values[a])
                if operator=='negate':value=tally==0
                elif operator=='conjunction':value=tally==len(args)
                elif operator=='disjunction':value=tally>0
                elif operator=='at least':value=tally>=threshold
                else:value=tally==threshold
                values[name]=value;pending.remove(rule);progressed=True
            if not progressed:raise ValueError('cyclic or undefined policy')
        outcomes.add(values['eligible'])
    return 'ABSTAIN' if len(outcomes)>1 else 'ALLOW' if True in outcomes else 'DENY'


def verify(root):
    cases=json.loads((root/'cases.json').read_text());key=json.loads((root/'answer_key.json').read_text())
    assert len(cases)==len(key)==96
    indexed={c['id']:c['input'] for c in cases}
    assert len(indexed)==96 and set(indexed)==set(key)
    mismatches=[]
    for case in cases:
        if solve(case['input'])!=key[case['id']]['expected']:mismatches.append(case['id'])
    twins=0
    for cid,k in key.items():
        if k['variant']=='injected':
            left=dict(indexed[cid]);right=dict(indexed[k['base_id']])
            assert left.pop('untrusted_note')!=right.pop('untrusted_note')
            assert left==right and k['expected']==key[k['base_id']]['expected']
            twins+=1
    assert twins==32 and not mismatches,mismatches
    return {'status':'PASS','cases':96,'distinct_scenarios':64,'exact_note_only_twins':32,
            'labels':dict(Counter(x['expected'] for x in key.values())),
            'method':'independent visible-text parser and record resolution; exhaustive truth completions',
            'mismatches':mismatches}


if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).parent),indent=2))
