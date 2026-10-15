"""Exact rational existence witnesses, not reconstruction of server internals."""
from fractions import Fraction as F
from decimal import Decimal as D
CENT=F(1,100); HALF=F(1,200); SHRINK=F(1,10**9); EPS=D('1e-12')

def witness(q,c,shrink=False):
    if any(v<0 or v>1 for v in q.values()) or q[c]<max(q.values()):return None
    lo={k:max(F(0),v-HALF) for k,v in q.items()};hi={k:min(F(1),v+HALF) for k,v in q.items()}
    if shrink:
        lo={k:v+(SHRINK if v>0 else 0) for k,v in lo.items()}
        hi={k:v-(SHRINK if v<1 else 0) for k,v in hi.items()}
    others=[k for k in q if k!=c]
    lower=max(lo[c],max(lo[k] for k in others))
    upper=min(hi[c],1-sum(lo[k] for k in others))
    if lower>upper or upper+sum(min(hi[k],upper) for k in others)<1:return None
    u={c:upper,**{k:lo[k] for k in others}};remaining=1-sum(u.values())
    for k in others:
        add=min(remaining,min(hi[k],upper)-u[k]);u[k]+=add;remaining-=add
    assert remaining==0 and sum(u.values())==1 and u[c]==max(u.values())
    assert all(lo[k]<=u[k]<=hi[k] for k in q)
    return u

def feasibility(q,c):
    u=witness(q,c,True)
    if u is not None:return {'status':'interior_compatible','latent_witness':u}
    u=witness(q,c,False)
    if u is not None:return {'status':'boundary_ambiguous','latent_witness':u}
    return {'status':'incompatible','latent_witness':None}

def classify(probabilities,choice):
    p={k:D(str(v)) for k,v in probabilities.items()};grid={k:v.quantize(D('.01')) for k,v in p.items()}
    if choice not in p or len(p) not in (2,3):raise ValueError('unsupported answer')
    ongrid=all(abs(p[k]-grid[k])<=EPS for k in p)
    base={'reported_grid':grid,'grid_total':sum(grid.values()),'on_hundredth_grid':ongrid,'raw_tail_labels':[k for k in p if p[k]!=grid[k]]}
    if not ongrid:return {**base,'plain':{'status':'incompatible','reason':'off_hundredth_grid'},'residual_status':'incompatible','residual_reason':'off_hundredth_grid','candidates':[],'nonzero_correction_required':False}
    q={k:F(v) for k,v in grid.items()};plain=feasibility(q,choice);candidates=[]
    reason=None
    if abs(sum(p.values())-1)>EPS:reason='reported_total_not_one'
    else:
        for delta in (-CENT,F(0),CENT):
            pre=dict(q);pre[choice]-=delta
            if delta!=1-sum(pre.values()):continue
            fit=feasibility(pre,choice)
            if fit['status']!='incompatible':candidates.append({'delta_to_selected':delta,'pre_correction_grid':pre,**fit})
        if not candidates:reason='no_feasible_latent_selected_maximum'
    status='interior_compatible' if any(c['status']=='interior_compatible' for c in candidates) else 'boundary_ambiguous' if candidates else 'incompatible'
    return {**base,'plain':plain,'residual_status':status,'residual_reason':reason,'candidates':candidates,'nonzero_correction_required':bool(candidates) and all(c['delta_to_selected']!=0 for c in candidates)}
