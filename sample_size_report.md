# Sample-size analysis

## Selected basis

The primary endpoint is the binary 30-minute risk of clinically important
peri-protamine hypotension. The planning control risk is
12.9%, anchored to a published 12.9% adverse-event
rate during the 30 minutes after protamine administration in patients undergoing
cardiopulmonary bypass. This external estimate does not use the identical endpoint,
so it is treated as a planning anchor rather than validation of the endpoint.
The treatment risk is 6.0%; this is materially
more conservative than the zero-event retrospective observation.

Using a two-sided alpha of 0.05, 90% power, equal
allocation, and the standard normal approximation for two independent
proportions gives 375.6 evaluable participants
per arm. Allowing 5% for cancelled surgery, absent protamine
exposure, or unusable arterial-line data gives
396 per arm
(792 total). The operational target is **800**
participants (400 per arm).

The formula is:

`n = [z_(1-alpha/2)*sqrt(2*p_bar*(1-p_bar)) + z_power*sqrt(p_c*(1-p_c)+p_t*(1-p_t))]^2 / (p_c-p_t)^2`.

## Sensitivity scenarios

The CSV includes all requested 17% versus 5%, 7%, and 8% scenarios at 80%
and 90% power, additional externally anchored scenarios, and continuous-outcome
scenarios for a 4.09-mmHg difference with standard deviations of 10, 12, and
15 mmHg. The binary endpoint determines the target sample size.

## Blinded internal reassessment

Because published protamine studies use heterogeneous event definitions, the
pooled primary-event rate will be reviewed after 300
participants have completed the primary window. A statistician who remains
blinded to treatment labels may update the nuisance event-rate assumption using
a prespecified algorithm without examining the treatment effect. Any increase
will require data-monitoring committee recommendation, sponsor approval, ethics
approval where required, registry amendment, and protocol-version control.
No unblinded treatment comparison will be used for this reassessment.
