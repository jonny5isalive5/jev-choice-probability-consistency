"""Frozen 100-call diagnostic. No retry, redirect, answer repair or secret logging."""
import json, hashlib, os, time, urllib.request, urllib.error
from pathlib import Path
from decimal import Decimal as D
from datetime import datetime, timezone

DESIGN=Path(r'evidence/Jev-Rounding100-Design-v1')
OUT=Path(r'evidence/Jev-Rounding100-Run-v1')
SOURCE=Path(__file__).parent
ENDPOINT='https://api.typesafe.ai/v1/systemone'
MODEL='jev-1.14.0'
RATE=D('0.000000042'); RESERVE=D(65536)*RATE*2
PRIOR=D('0.447300588'); LIMIT=D(5)
HEADERS=('x-typesafe-request-id','date','content-type','x-request-id','x-model-version','x-model-fingerprint','x-typesafe-model-version','x-typesafe-model-fingerprint','x-cache','cf-cache-status','age')

class Stop(Exception): pass
def now(): return datetime.now(timezone.utc).isoformat()
def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def save(p,x):
    with Path(p).open('xb') as f:
        f.write(json.dumps(x,indent=2,default=str,allow_nan=False).encode()+b'\n'); f.flush(); os.fsync(f.fileno())
def append(p,x):
    with Path(p).open('ab') as f:
        f.write(json.dumps(x,default=str,allow_nan=False).encode()+b'\n'); f.flush(); os.fsync(f.fileno())
def strict(raw):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d: raise Stop('duplicate JSON key')
            d[k]=v
        return d
    def bad(x): raise Stop('nonfinite number')
    return json.loads(raw,parse_float=D,parse_constant=bad,object_pairs_hook=pairs)
def numeric(x): return type(x) in (D,int) and D(x).is_finite() and 0<=x<=1

def extract(raw, labels):
    r=strict(raw)
    if not isinstance(r,dict) or r.get('model')!=MODEL: raise Stop('unexpected model')
    u=r.get('usage',{})
    if not isinstance(u,dict) or any(type(u.get(k)) is not int or u[k]<0 for k in ('input_tokens','output_tokens')): raise Stop('invalid usage')
    if u['input_tokens']>65536: raise Stop('usage exceeds reserve')
    ans=r.get('answers')
    if not isinstance(ans,dict) or set(ans)!={'decision'}: raise Stop('wrong question IDs')
    a=ans['decision']
    if not isinstance(a,dict) or a.get('type')!='choice': raise Stop('wrong answer type')
    p=a.get('probabilities'); c=a.get('choice'); conf=a.get('confidence')
    if not isinstance(p,dict) or set(p)!=set(labels): raise Stop('wrong probability labels')
    if any(not numeric(v) for v in p.values()) or not numeric(conf): raise Stop('invalid probability/confidence')
    if not isinstance(c,str) or c not in p: raise Stop('choice outside options')
    p={k:D(v) for k,v in p.items()}; conf=D(conf)
    n=D(len(p)); baseline=1/n; scale=1/(1-baseline)
    peak=max(p.values()); gap=peak-p[c]; tops=sorted(k for k,v in p.items() if v==peak)
    # Intervals are descriptive nearest-hundredth assumptions, not repairs.
    lo={k:max(D(0),v-D('.005')) for k,v in p.items()}
    hi={k:min(D(1),v+D('.005')) for k,v in p.items()}
    conf_lo=max(D(0),conf-D('.005')); conf_hi=min(D(1),conf+D('.005'))
    formula_lo=max(D(0),(max(lo.values())-baseline)*scale)
    formula_hi=min(D(1),(max(hi.values())-baseline)*scale)
    return {'model':r['model'],'usage':u,'choice':c,'probabilities':p,'confidence':conf,'max_labels':tops,
      'gap':gap,'mismatch':gap>0,'original_tolerance_mismatch':gap>D('.000001'),'tie':len(tops)>1,
      'mass':sum(p.values()),'hundredth_grid':all(abs(v-v.quantize(D('.01')))<=D('1e-12') for v in p.values()),
      'nearest_hundredth_mass_compatible':sum(lo.values())<=1<=sum(hi.values()),
      'confidence_formula_from_reported':(peak-baseline)*scale,
      'confidence_formula_delta':conf-((peak-baseline)*scale),
      'nearest_hundredth_confidence_intervals_overlap':max(conf_lo,formula_lo)<=min(conf_hi,formula_hi)}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None
class Transport:
    def __init__(self,secret):
        self.secret=secret; self.opener=urllib.request.build_opener(NoRedirect())
    def __call__(self,payload):
        req=urllib.request.Request(ENDPOINT,payload,method='POST',headers={'Authorization':'Bearer '+self.secret,'Content-Type':'application/json'})
        try:
            try: response=self.opener.open(req,timeout=30)
            except urllib.error.HTTPError as e: response=e
            with response as r:
                raw=r.read(1024*1024+1)
                headers={k:r.headers.get(k) for k in HEADERS}
                status=r.status
        except Exception as e: raise Stop('transport failure: '+type(e).__name__) from None
        # A provider echo of a credential must never reach disk.
        leaked=self.secret.encode() in raw or any(self.secret in v for v in headers.values() if v)
        if leaked:
            raw=raw.replace(self.secret.encode(),b'[REDACTED]')
            headers={k:v.replace(self.secret,'[REDACTED]') if v else v for k,v in headers.items()}
        return status,headers,raw,leaked

def collect(transport,folder,schedule,payloads,ceiling=LIMIT):
    folder.mkdir(exist_ok=False)
    held=PRIOR; cost=D(0); usable=0; attempts=0; reason=None
    for entry in schedule:
        if attempts>=100 or held+RESERVE>ceiling:
            reason='budget or attempt ceiling'; break
        payload=payloads[entry['payload']]
        p=folder/f"{entry['attempt']:04d}"; p.mkdir()
        (p/'request.json').write_bytes(payload)
        start=now(); t=time.monotonic(); attempts+=1; held+=RESERVE
        meta={**entry,'started_utc':start,'request_sha256':sha(payload),'semantic_sha256':sha(canonical(json.loads(payload))),
              'endpoint':ENDPOINT,'reserve_gbp':str(RESERVE),'accounted_gbp':str(held)}
        save(p/'attempt.json',meta); append(folder/'ledger.jsonl',{'event':'reserve',**meta})
        try:
            status,headers,raw,redacted=transport(payload)
            (p/'response.body').write_bytes(raw)
            save(p/'http.json',{'status':status,'headers':headers,'ended_utc':now(),'latency_seconds':time.monotonic()-t,'response_sha256':sha(raw),'secret_echo_redacted':redacted,'over_1MiB':len(raw)>1024*1024})
            if redacted: raise Stop('credential echo redacted; response unusable')
            if len(raw)>1024*1024: raise Stop('response too large; saved bounded prefix')
            if status!=200: raise Stop('HTTP '+str(status))
            result=extract(raw, json.loads(payload)['questions']['decision']['criteria'])
            usd=D(result['usage']['input_tokens'])*RATE
            held=held-RESERVE+usd*2; cost+=usd; usable+=1
            save(p/'observation.json',result)
            append(folder/'ledger.jsonl',{'event':'settled','attempt':entry['attempt'],'utc':now(),'cost_usd':str(usd),'accounted_gbp':str(held)})
        except Exception as e:
            reason=str(e) if isinstance(e,Stop) else 'collector failure: '+type(e).__name__
            save(p/'failure.json',{'reason':reason,'utc':now(),'reserve_retained_gbp':str(RESERVE)})
            append(folder/'ledger.jsonl',{'event':'halt','attempt':entry['attempt'],'reason':reason,'accounted_gbp':str(held)})
            break
        if attempts%20==0: print(json.dumps({'completed':attempts,'of':len(schedule),'cost_usd':str(cost)}),flush=True)
    summary={'started':attempts>0,'attempts':attempts,'usable':usable,'planned':len(schedule),'complete':usable==len(schedule),'stop_reason':reason,'validated_usage_cost_usd':str(cost),'guard_accounted_gbp_including_prior':str(held),'prior_guard_gbp':str(PRIOR),'utc':now()}
    save(folder/'execution.json',summary); return summary

def verify_manifest(root,manifest):
    for name,h in manifest.items():
        if sha((root/name).read_bytes())!=h: raise Stop('hash mismatch: '+name)

def main():
    freeze=json.loads((SOURCE/'freeze.json').read_text()); verify_manifest(SOURCE,freeze['files'])
    df=json.loads((DESIGN/'DESIGN_FREEZE.json').read_text()); verify_manifest(DESIGN,df['files'])
    if sha((DESIGN/'DESIGN_FREEZE.json').read_bytes())!='6291d64a9b81a7def41862bd09bbf513c588231694967a58c073d2e047cebf0f': raise Stop('design seal changed')
    before=json.loads((OUT/'protected-before.json').read_text())
    for p,h in before.items():
        if sha(Path(p).read_bytes())!=h: raise Stop('protected file changed before execution')
    from secure_credential import credential
    secret=credential()
    if not secret: raise Stop('authorized named credential unavailable')
    schedule=json.loads((DESIGN/'schedule.json').read_text())
    manifest=json.loads((DESIGN/'payload-manifest.json').read_text())
    payloads={k:(DESIGN/v['path']).read_bytes() for k,v in manifest.items()}
    assert len(schedule)==100 and PRIOR+RESERVE*100<LIMIT
    print(json.dumps(collect(Transport(secret),OUT/'live-run-001',schedule,payloads)),flush=True)

if __name__=='__main__':
    try: main()
    except Exception as e:
        print('STOP: '+(str(e) if isinstance(e,Stop) else type(e).__name__),flush=True)
        raise SystemExit(1)
