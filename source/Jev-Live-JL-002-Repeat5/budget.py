"""One sequential, durable GBP ceiling across all five repetitions."""
import datetime
import json
import os
from decimal import Decimal
from pathlib import Path
from jev import Stop,canonical,strict_json,validate,RATE_USD,CALL_RESERVE,GBP_PER_USD_RESERVE


def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()


class SharedBudget:
    def __init__(self,path,historical_usd,max_calls=4325,ceiling=Decimal(5)):
        self.path=Path(path);self.path.touch(exist_ok=False)
        self.historical_usd=Decimal(historical_usd);self.new_usd=Decimal(0)
        self.accounted_gbp=self.historical_usd*GBP_PER_USD_RESERVE
        self.calls=0;self.max_calls=max_calls;self.ceiling=ceiling
        self.halted=False;self.pending=False
        self.record(event='opened',historical_usd=str(self.historical_usd),ceiling_gbp=str(ceiling),max_calls=max_calls)

    def record(self,**event):
        event.update(utc=utc(),global_sequence=self.calls,accounted_gbp=str(self.accounted_gbp))
        with self.path.open('ab') as f:f.write(canonical(event)+b'\n');f.flush();os.fsync(f.fileno())

    def reserve(self,rep):
        if self.halted or self.pending:raise Stop('shared budget halted or unresolved reservation')
        if self.calls>=self.max_calls:raise Stop('shared request ceiling reached before dispatch')
        if self.accounted_gbp+CALL_RESERVE>self.ceiling:raise Stop('shared GBP ceiling reached before dispatch')
        self.calls+=1;self.accounted_gbp+=CALL_RESERVE;self.pending=True
        self.record(event='reserved',repeat=rep,reserve_gbp=str(CALL_RESERVE))

    def settle(self,response,rep):
        if not self.pending:raise Stop('no pending reservation')
        cost=Decimal(response['usage']['input_tokens'])*RATE_USD
        self.accounted_gbp+=cost*GBP_PER_USD_RESERVE-CALL_RESERVE
        self.new_usd+=cost;self.pending=False
        self.record(event='settled',repeat=rep,input_tokens=response['usage']['input_tokens'],listed_usd=str(cost))

    def retain(self,rep,reason):
        self.halted=True
        self.record(event='unresolved_retained',repeat=rep,reason=reason)

    def snapshot(self):
        return {'new_attempts':self.calls,'new_listed_usd':str(self.new_usd),
                'historical_listed_usd':str(self.historical_usd),
                'combined_listed_usd':str(self.historical_usd+self.new_usd),
                'accounted_gbp_at_conservative_rate':str(self.accounted_gbp),
                'hard_ceiling_gbp':str(self.ceiling),'pending_reservation':self.pending,'halted':self.halted}


class BudgetTransport:
    def __init__(self,inner,budget,rep):
        self.inner,self.budget,self.rep=inner,budget,rep
        self.genuine=inner.genuine

    def __call__(self,payload):
        self.budget.reserve(self.rep)
        try:status,raw=self.inner(payload)
        except Exception as exc:
            self.budget.retain(self.rep,type(exc).__name__)
            raise
        try:
            if status!=200:raise Stop('non-200 response')
            response=validate(strict_json(raw),strict_json(payload))
        except Exception as exc:
            # Return the original response so the unchanged adapter preserves it.
            self.budget.retain(self.rep,type(exc).__name__)
            return status,raw
        self.budget.settle(response,self.rep)
        return status,raw
