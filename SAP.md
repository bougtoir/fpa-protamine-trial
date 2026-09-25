
# Statistical Analysis Plan

Version 1.0; dated 2026-09-25. Finalise and sign before database lock and before treatment codes are released.

## Objectives and estimands

The primary objective is to estimate the effect of assignment to FPA versus placebo on clinically important peri-protamine hypotension. The primary estimand is a treatment-policy risk difference in all randomised participants, regardless of adherence, crossover, rescue treatment, or protocol deviation, except that participants randomised in error who never undergo surgery/protamine remain in the ITT denominator with endpoint status handled under the missing-data rules.

## Analysis populations

- **ITT:** all randomised participants, analysed as assigned.
- **Safety:** all participants receiving any study drug, analysed as treated.
- **Per protocol:** study drug administered as assigned; dose 45–55 mg or placebo-equivalent volume; infusion duration 4–6 minutes; completion 10–20 minutes before t=0; eligible surgery; no prohibited unblinding; evaluable waveform.

## Primary analysis

Fit logistic regression with treatment, site stratum, prior protamine/protamine-insulin exposure, and continuous baseline MAP. Standardise predicted risks over the ITT population. Report marginal risk difference and risk ratio with two-sided 95% CIs; the primary CI for the risk difference uses the 2.5th and 97.5th percentiles of 2,000 stratified bootstrap samples. Also report crude risks and odds ratio. Statistical significance uses two-sided alpha 0.05.

If complete or quasi-complete separation occurs, use Firth penalised logistic regression for conditional estimates and report an exact unconditional risk difference interval as a sensitivity analysis. Model convergence, influential observations, calibration, and functional form of baseline MAP will be checked.

## Intercurrent events and missing data

Rescue vasoactive treatment, fluids, pacing, cardioversion, return to CPB, and mechanical support are not censored in the treatment-policy primary analysis. A supportive composite counts the MAP criterion, protocol-defined rescue, return to CPB, or rescue mechanical support. Crossovers remain analysed as randomised.

No waveform-second imputation is used to derive the endpoint. If the endpoint is missing in ≤1% of the ITT population, complete-case primary analysis plus best/worst-case bounds will be reported. If >1%, multiple imputation by chained equations will include treatment, strata, baseline MAP, surgery type, CPB duration, rescue treatment, and observed haemodynamic summaries; Rubin’s rules combine estimates. Missing continuous secondary outcomes use analogous multiple imputation when plausible.

## Secondary analyses

- Binary outcomes: risk difference and risk ratio with 95% CIs.
- Nadir MAP, relative MAP decline, and hypotension burden: ANCOVA/linear regression adjusted for randomisation strata and baseline MAP; inspect residuals and use transformation or robust regression if assumptions materially fail.
- Repeated minute-level MAP: supportive mixed model with fixed treatment, time, treatment-by-time, baseline MAP, strata, and participant random intercept; model covariance selected before unmasking.
- Time to first endpoint: Kaplan–Meier description and stratified Cox model only as supportive analysis.
- Safety: denominators, risks, risk differences, and exact 95% CIs; sparse outcomes are descriptive.

## Multiplicity and subgroups

The primary endpoint has one confirmatory test. All secondary outcomes and interactions are supportive; no adjusted efficacy claims will be made. Prespecified exploratory subgroups are prior protamine/protamine-insulin exposure, surgery class, baseline MAP, CPB duration, sex, and site region. Report interaction estimates and CIs, not within-subgroup significance claims.

## Sample size and blinded reassessment

The design assumes placebo risk 12.9%, FPA risk 6.0%, two-sided alpha 0.05, power 90%, and 5% non-evaluable allowance. Executable calculations require at least 792 participants; the operational target is 800 (400 per group). The 12.9% anchor derives from a broader external protamine-adverse-event definition and does not validate this protocol’s endpoint.

After 300 participants, an independent statistician may update only the pooled primary-event and non-evaluable rates while preserving the planned absolute effect assumption and treatment masking. The target may increase to maintain 90% power, subject to a prespecified cap of 1,200; it will not decrease below 800. No treatment-effect estimate is released.
