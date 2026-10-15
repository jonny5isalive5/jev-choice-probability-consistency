import json
from pathlib import Path

BASE=Path('evidence/Jev-Live-JL-002-Repeat5')
ROOT=Path('source/Jev-Live-JL-002-Repeat5')
a=json.loads((BASE/'evidence/repeatability.json').read_text())
audit=json.loads((BASE/'evidence/final-audit.json').read_text())
freeze=json.loads((ROOT/'freeze.json').read_text())
arms=('single','swarm','sequential')
lines=['# JL-002 Repeat5: repeatability on the same frozen 96 cases','',
       f"Completed new repetitions: **{a['complete_new_repeats']}/5**. Original reference is separate.",
       'All new inference responses are from the direct TypeSafe API. The original JS and JL runs remain untouched.','',
       '## Primary comparison: 64 distinct clean base cases','',
       '| Run | Single correct | Swarm correct | Sequential correct | Swarm minus sequential | False authorizations: single / swarm / sequential | Frozen favorable screen |',
       '|---|---:|---:|---:|---:|---|---|']

def row(label,r,scope='clean_64'):
    values=[r['arms'][arm][scope]['correct'] for arm in arms]
    fa=[r['arms'][arm][scope]['false_authorizations'] for arm in arms]
    return f"| {label} | {values[0]} | {values[1]} | {values[2]} | {values[1]-values[2]:+d} | {' / '.join(map(str,fa))} | {'PASS' if r['predeclared_favorable_descriptive_signal'] else 'FAIL'} |"

lines.append(row('Original JL-002-R1',a['original_reference']))
for r in a['repeats']:
    if 'arms' in r:lines.append(row(f"Repeat {r['repeat']} ({r['status'].lower()})",r))
    else:lines.append(f"| Repeat {r['repeat']}: {r['status']} | — | — | — | — | — | — |")
direction=a['primary_direction_counts']
lines += ['',f"Across completed new repeats: swarm ahead **{direction.get('swarm_ahead',0)}**, tied **{direction.get('tie',0)}**, sequential ahead **{direction.get('sequential_ahead',0)}**.",
          f"The unchanged favorable-result screen passed in **{a['predeclared_favorable_count']}/{a['complete_new_repeats']}** completed repeats. It requires at least four net additional correct base cases and no deterioration in the declared controls. An accuracy lead alone is insufficient.",
          '', 'The original and every new repeat are retained. No repetition was selected, dropped, replaced, or extended because of its scores.', '',
          '| Arm | New-repeat primary counts | Mean correct / 64 | Range |',
          '|---|---|---:|---|']
for arm in arms:
    d=a['clean_accuracy_distribution'][arm]
    mean=f"{d['mean']:.2f}" if d['mean'] is not None else '—'
    lines.append(f"| {arm.title()} | {', '.join(map(str,d['values']))} | {mean} | {d['minimum']}–{d['maximum']} |")
lines += ['', '## Secondary comparison: all 96 cases','',
          'These include 32 correlated injection twins. They are not 96 independent base questions.','',
          '| Run | Single correct | Swarm correct | Sequential correct | Swarm minus sequential | False authorizations: single / swarm / sequential | Frozen primary screen |',
          '|---|---:|---:|---:|---:|---|---|',row('Original JL-002-R1',a['original_reference'],'all_96')]
for r in a['repeats']:
    if 'arms' in r:lines.append(row(f"Repeat {r['repeat']}",r,'all_96'))
lines += ['', '## Controls and abstentions','',
          '| Run / arm | Clean false authorizations | Injected false authorizations | Clean wrong abstentions | All abstentions | Injection correct-to-wrong |',
          '|---|---:|---:|---:|---:|---:|']
for r in a['repeats']:
    if 'arms' not in r:continue
    for arm in arms:
        m=r['arms'][arm]
        lines.append(f"| {r['repeat']} / {arm} | {m['clean_64']['false_authorizations']} | {m['injected_32']['false_authorizations']} | {m['clean_64']['wrong_abstentions']} | {m['all_96']['abstentions']} | {r['paired_injection_effects'][arm]['correct_to_wrong']} |")
lines += ['', '## Stability of individual answers','',
          '| Run | Same final choices as original: single / swarm / sequential (out of 96 each) | Same full final answers, including probabilities/confidence |',
          '|---|---|---|']
for r in a['repeats']:
    if 'agreement_with_original' not in r:continue
    g=r['agreement_with_original']
    lines.append(f"| {r['repeat']} | {' / '.join(str(g[arm]['same_final_choice']) for arm in arms)} | {' / '.join(str(g[arm]['same_full_final_answer']) for arm in arms)} |")
if a['complete_new_repeats']==5:
    lines += ['', 'Number of case/arm results whose final choice varied among the five new runs: '+', '.join(f"{arm} **{len(a['cases_with_changing_final_choices'][arm])}/96**" for arm in arms)+'.']
lines += ['', 'Detailed changing-case lists and all ten pairwise repeat comparisons are saved in `evidence/repeatability.json`. Equal aggregate scores do not imply identical case-level decisions.', '',
          '| Repeat | Requests byte-identical to original | Different typed answers on those identical requests | Different choices on those identical requests | Largest probability difference |',
          '|---|---:|---:|---:|---:|']
for r in audit['repeats']:
    if 'attempts' not in r:continue
    lines.append(f"| {r['repeat']} | {r['historical_reference_payloads_identical']} | {r['different_answers_on_identical_payloads']} | {r['different_choices_on_identical_payloads']} | {r['maximum_probability_change_on_identical_payload']} |")
lines += ['', 'Later sequential and synthesis requests legitimately vary when fresh intermediate judgments vary. Frozen prompts, original evidence and scheduling remain identical; previous-run judgments are never substituted. Service caching, backend hardware and internal sampling are not controlled by this client. Identical observations would not prove universal determinism.', '',
          '## Usage and shared spending guard','',
          '| Repeat | Inference calls | Input tokens | Output tokens | Published-price USD cost |',
          '|---|---:|---:|---:|---:|']
for r in audit['repeats']:
    if 'attempts' not in r:continue
    lines.append(f"| {r['repeat']} | {r['attempts']} | {r['input_tokens']:,} | {r['output_tokens']:,} | {r['listed_usd']} |")
lines += [f"| New total | {audit['new_inference_attempts']} | {audit['new_validated_input_tokens']:,} | {audit['new_validated_output_tokens']:,} | **{audit['new_listed_usd']}** |",'',
          f"New reported usage costs approximately **GBP {float(audit['new_gbp_estimate_prior_reference']):.5f}**, using the earlier recorded GBP 0.7604301892533474/USD reference. This is not a settled invoice or a current FX quote.",
          '[TypeSafe pricing](https://docs.typesafe.ai/models), rechecked before execution: USD 0.042 per million input tokens; output tokens free. No other paid service was used.', '',
          f"The single shared GBP 5 guard additionally carries prior JL-001 and complete JL-002-R1 costs of USD {audit['historical_listed_usd_in_guard']}, counted once. Combined listed USD cost including that history: **{audit['combined_usd_in_guard']}**.",
          f"At its conservative GBP 2/USD allowance, the maximum balance including any in-flight full-context reservation was **GBP {audit['maximum_accounted_gbp_including_inflight_reservations']}**, below GBP 5. The final balance including prior runs was GBP {audit['final_accounted_gbp_including_prior_runs']}.",
          'Before each request the journal reserves the maximum documented default context. Only a validated response permits settlement to actual reported usage; uncertain reservations remain charged and stop the batch. The five local per-run full-context reservation totals are not added as actual spending. `budget.jsonl` is the shared accounting evidence.', '',
          '## Freeze, verification and preservation','',
          f"Source and repeatability protocol frozen at **{freeze['frozen_utc']}** before new live inference. Eight engineering tests passed, including replay of all 865 original requests and exact reproduction of the saved original predictions without network calls.",
          'Ten inherited files, including the R1 adapter, arm execution, scorer, cases, answer key, prompts and original protocol, are byte-identical. The separate repeat protocol fixes five runs, the same ordering, all-result retention, analysis and stopping rules. No scores were inspected between repetitions.',
          f"The final audit checked **{audit['original_files_checked']} protected original files**: zero changes. All completed-run request schedules, histories, raw response hashes, prediction seals and shared-budget entries reconciled. No plaintext credential was found in the created source or evidence.",
          f"Returned model counts: `{audit['reported_models']}`. The pinned model is `jev-1.14.0`; no independent server fingerprint is supplied. Automatic retries: **0**. Batch stop reason: `{audit['stopped']}`.",
          'The R1 rounding policy was retained unchanged. Per-run sequences using its narrow allowance, plus any errors and partial cases, are retained in `evidence/final-audit.json` and each raw ledger.', '',
          '## Interpretation and next action','',
          'These repetitions measure observed stability on the same 64 distinct base questions and 32 correlated twins. They are not five new benchmark datasets or 320 independent base questions. The fixtures and original outcomes were already visible. The same four policy templates and task-fit limitations remain.',
          'Swarm and sequential each receive four calls per case with identical evidence and checklists; only preceding-judgment visibility differs. Actual tokens and cost may differ. Single remains a one-call lower-cost reference. Outputs are typed choices and probabilities, not prose chain-of-thought. No statistical significance, general safety or emergent-intelligence claim is made.',
          '**STOP at this five-repeat checkpoint.** Retain every result. Do not select a favorable run, tune this frozen set, automatically rerun errors, or infer general superiority from small within-set leads.', '',
          'Source: `source/Jev-Live-JL-002-Repeat5`.',
          'Evidence: `evidence/Jev-Live-JL-002-Repeat5`.',
          'Key artifacts: `repeat_protocol.json` and all source in `source-before-live.zip`; `evidence/repeatability.json`; `evidence/final-audit.json`; each `evidence/live-batch/repeat-01` through `repeat-05` with requests, responses, sealed predictions, execution record and unchanged-scoring result; `evidence/live-batch/budget.jsonl` and `batch.json`; protection manifest and unit-test record.',
          'Offline analysis entry point: `python -B analyze.py` from the new source directory. Do not invoke inherited historical CLI entry points or launch additional live runs.','']
(BASE/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
print(str(BASE/'RESULTS.md'))
