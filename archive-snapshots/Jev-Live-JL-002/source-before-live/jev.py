"""JL-002 direct TypeSafe Choice adapter. No SDK retries, redirects or secret logs."""
import hashlib
import json
import math
import os
import urllib.error
import urllib.request
from decimal import Decimal
from pathlib import Path

MODEL = 'jev-1.14.0'
ENDPOINT = 'https://api.typesafe.ai/v1/systemone'
RATE_USD = Decimal('0.042') / Decimal(1000000)
MAX_INPUT = 65536  # conservatively covers documented default 64k; no long-context header
MAX_CALLS = 865   # one smoke + 96 * (1 + 4 + 4); zero retries
GBP_PER_USD_RESERVE = Decimal('2')  # conservative allowance, NOT an exchange-rate quote
CALL_RESERVE = Decimal(MAX_INPUT) * RATE_USD * GBP_PER_USD_RESERVE


class Stop(RuntimeError):
    pass


# Reused mechanism: canonical JSON + SHA-256, from frozen JS-003 wire.py.
# No import, runtime patch, synthetic policy, fixed-byte frame or oracle is reused.
def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Stop('duplicate JSON key')
            result[key] = value
        return result
    def bad_number(value):
        raise Stop('nonfinite JSON number')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad_number)


def credential():
    """Read only named authorized environment settings; never copy to files."""
    for name in ('TYPESAFE_API_KEY', 'JEV_API_KEY'):
        value = os.environ.get(name, '').strip()
        if value:
            return value
    if os.name == 'nt':
        import winreg
        for hive, path in ((winreg.HKEY_CURRENT_USER, 'Environment'),
                           (winreg.HKEY_LOCAL_MACHINE,
                            r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment')):
            try:
                with winreg.OpenKey(hive, path) as key:
                    for name in ('TYPESAFE_API_KEY', 'JEV_API_KEY'):
                        try:
                            value, kind = winreg.QueryValueEx(key, name)
                            if kind in (winreg.REG_SZ, winreg.REG_EXPAND_SZ) and value.strip():
                                return value.strip()
                        except FileNotFoundError:
                            pass
            except FileNotFoundError:
                pass
    return None


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate(response, request):
    if not isinstance(response, dict) or response.get('model') != MODEL:
        raise Stop('model version missing or changed')
    usage = response.get('usage', {})
    for field in ('input_tokens', 'output_tokens'):
        if type(usage.get(field)) is not int or usage[field] < 0:
            raise Stop('missing or invalid usage')
    if usage['input_tokens'] > MAX_INPUT:
        raise Stop('usage exceeds reserved default context')
    answers = response.get('answers')
    if not isinstance(answers, dict) or set(answers) != set(request['questions']):
        raise Stop('answer IDs differ from question IDs')
    for key, question in request['questions'].items():
        a = answers[key]
        if not isinstance(a, dict) or a.get('type') != 'choice':
            raise Stop('wrong answer type')
        probabilities = a.get('probabilities', {})
        if set(probabilities) != set(question['criteria']):
            raise Stop('probability option mismatch')
        if any(not number(v) or not 0 <= v <= 1 for v in probabilities.values()):
            raise Stop('invalid probability')
        if abs(sum(probabilities.values()) - 1) > 0.001:
            raise Stop('probabilities do not sum to one')
        if a.get('choice') not in probabilities:
            raise Stop('choice outside answer space')
        if probabilities[a['choice']] + 1e-6 < max(probabilities.values()):
            raise Stop('choice is not a probability maximum')
        if not number(a.get('confidence')) or not 0 <= a['confidence'] <= 1:
            raise Stop('invalid confidence')
    return response


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HTTPTransport:
    genuine = True

    def __init__(self, secret):
        self._secret = secret
        self._opener = urllib.request.build_opener(NoRedirect())

    def __call__(self, payload):
        request = urllib.request.Request(ENDPOINT, payload, method='POST', headers={
            'Authorization': 'Bearer ' + self._secret, 'Content-Type': 'application/json'})
        try:
            with self._opener.open(request, timeout=30) as r:
                raw = r.read(1024 * 1024 + 1)
                status = r.status
        except urllib.error.HTTPError as exc:
            status, raw = exc.code, exc.read(1024 * 1024 + 1)
        except Exception as exc:
            # Never serialize the exception text, Request, headers, or secret.
            raise Stop('transport failure: ' + type(exc).__name__) from None
        raw = raw.replace(self._secret.encode(), b'[REDACTED]')
        if len(raw) > 1024 * 1024:
            raise Stop('response too large')
        return status, raw


class MockTransport:
    """Contract fixture only: intentionally not an intelligence simulation or oracle."""
    genuine = False

    def __call__(self, payload):
        request = strict_json(payload)
        answers = {}
        for key, q in request['questions'].items():
            options = q['criteria']
            choice = 'ABSTAIN' if 'ABSTAIN' in options else next(iter(options))
            answers[key] = {'type': 'choice', 'choice': choice, 'confidence': 1.0,
                            'probabilities': {o: float(o == choice) for o in options}}
        response = {'model': MODEL, 'answers': answers,
                    'usage': {'input_tokens': len(payload), 'output_tokens': 100}}
        return 200, canonical(response)


class Client:
    def __init__(self, transport, directory, max_calls=MAX_CALLS):
        if type(max_calls) is not int or not 1 <= max_calls <= MAX_CALLS:
            raise Stop('invalid call ceiling')
        self.transport, self.max_calls = transport, max_calls
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.ledger = self.directory / 'ledger.jsonl'
        self.calls = 0
        self.reserved = Decimal(0)
        self.actual_usd = Decimal(0)
        self.halted = False
        self.arm_calls = {}

    def append(self, event):
        with self.ledger.open('ab') as f:
            f.write(canonical(event) + b'\n')
            f.flush()
            os.fsync(f.fileno())

    def call(self, request, case_id, arm, stage):
        if self.halted:
            raise Stop('client halted after previous failure')
        if set(request) != {'model', 'state', 'questions'} or request['model'] != MODEL:
            raise Stop('invalid request envelope')
        if not request['questions'] or any(q.get('type') != 'choice' or
                set(q) != {'type', 'instructions', 'criteria'} or
                not 1 <= len(q['criteria']) <= 255 for q in request['questions'].values()):
            raise Stop('invalid Choice request')
        payload = canonical(request)
        if len(payload) > 16000:
            raise Stop('request exceeds frozen local size limit')
        slot = (case_id, arm)
        if self.arm_calls.get(slot, 0) >= 4 or self.calls >= self.max_calls:
            raise Stop('request ceiling reached before dispatch')
        if self.reserved + CALL_RESERVE > Decimal('5'):
            raise Stop('GBP ceiling reached before dispatch')
        self.calls += 1
        self.arm_calls[slot] = self.arm_calls.get(slot, 0) + 1
        self.reserved += CALL_RESERVE  # never refund uncertain/failed attempts
        identity = {'sequence': self.calls, 'case_id': case_id, 'arm': arm, 'stage': stage}
        self.append(dict(identity, event='reserved', request=request,
                         request_sha256=digest(request), genuine=self.transport.genuine,
                         gbp_reserved_total=str(self.reserved)))
        try:
            status, raw = self.transport(payload)
            (self.directory / f'response-{self.calls:04}.json').write_bytes(raw)
            self.append(dict(identity, event='received', http_status=status,
                             response_sha256=hashlib.sha256(raw).hexdigest()))
            if status != 200:
                raise Stop('HTTP ' + str(status) + '; no retry')
            response = validate(strict_json(raw), request)
            cost = Decimal(response['usage']['input_tokens']) * RATE_USD
            self.actual_usd += cost
            self.append(dict(identity, event='validated', response=response,
                             listed_usage_cost_usd=str(cost)))
            return response['answers']
        except Exception as exc:
            self.halted = True
            # Our Stop messages contain no remote content or secret values.
            message = str(exc) if isinstance(exc, Stop) else type(exc).__name__
            self.append(dict(identity, event='stopped', reason=message))
            raise Stop(message) from None
