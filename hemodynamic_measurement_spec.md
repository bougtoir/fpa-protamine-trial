
# Haemodynamic measurement specification

## Time origin and acquisition

- `t=0` is the timestamp at which the first protamine infusion starts.
- Capture the arterial-pressure waveform at ≥1 Hz from at least −5 through +30 minutes relative to t=0.
- Record monitor time synchronisation, transducer level/zero confirmation, line site, and monitor/export system.
- The stabilised baseline MAP is the median of valid MAP observations from −5 to −1 minutes.

## Primary endpoint derivation

Compute a rolling 60-second median across the 0–30-minute window. A window is evaluable when at least 45 seconds are valid. The primary event occurs if at least one evaluable window has median MAP ≤80% of baseline. Exact equality qualifies.

## Supporting derivations

- MAP <65 mmHg: at least one evaluable 60-second window below 65 mmHg.
- Nadir MAP: minimum valid rolling 60-second median.
- Relative maximum decline: `(baseline MAP − nadir MAP) / baseline MAP`.
- Time under 65 mmHg: sum of valid seconds below 65, divided by 60.
- Area under 65 mmHg: integral of `max(65 − MAP, 0)` over valid time.
- Time-weighted MAP: area under the observed MAP curve divided by valid observation duration.

## Concomitant treatment

Record every vasopressor/inotrope bolus and infusion-rate change with exact time, drug, dose, and route from −10 through +30 minutes. Record fluids, pacing, cardioversion, return to CPB, mechanical support, and surgical events. The primary treatment-policy estimand uses observed MAP after rescue; a prespecified composite counts qualifying rescue as an event.
