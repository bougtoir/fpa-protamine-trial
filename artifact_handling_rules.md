
# Arterial-waveform artifact handling rules

## Automated flags

Mark a second invalid if MAP is physiologically impossible (<20 or >180 mmHg), the signal is absent, the arterial line is documented as disconnected/occluded, or the monitor identifies a flush/calibration event. Automated flags do not replace blinded adjudication.

## Flushes, damping, and isolated beats

- Exclude square-wave flush periods from five seconds before the flush until the waveform returns to interpretable pulsatility.
- Exclude documented blood sampling, line opening, transducer zeroing, and reconnection.
- Exclude clearly overdamped/underdamped periods when the waveform is nonphysiologic and corroborated by the site record or blinded central review.
- Do not classify a single-beat spike or trough as hypotension. The primary endpoint uses rolling 60-second medians and requires ≥45 valid seconds.
- Preserve true arrhythmia-associated pressure variation unless the waveform itself is uninterpretable.

## Treatment-induced measurements

Do not censor values after rescue vasopressor, fluid, pacing, cardioversion, or return to CPB in the primary treatment-policy analysis. Record interventions precisely. A composite sensitivity endpoint counts protocol-defined rescue, and supportive analyses will describe MAP before rescue.

## Missingness

The primary endpoint is non-evaluable when baseline has <180 valid seconds or the post-protamine window has <80% valid seconds after documented artifact exclusion. Do not impute waveform seconds for the primary derivation. Primary ITT analysis will use multiple imputation for a missing binary endpoint only if missingness exceeds 1%; best/worst-case bounds and complete-case analyses will be reported. Death or rescue mechanical support before endpoint ascertainment counts as an event.
