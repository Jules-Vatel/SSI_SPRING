# Pre-Analysis Plan: Partisan Reactions to Democratic Backsliding

## 1. Overview

This pre-analysis plan (PAP) covers a survey experiment on public reactions to democratic backsliding by state governors. The central theoretical aim is to study the causal arrow running from democratic backsliding to mass affective polarization and tolerance for future backsliding, rather than only the more familiar possibility that affective polarization enables antidemocratic behavior. The instrument randomly varies whether the governor belongs to the respondent's in-party or out-party and, in treated conditions, whether the action is justified using a policy, electoral-retaliation, or democracy-protection frame.

The current PAP is based on the survey instrument in `SSI_2026_MehlhaffOffer-Westort.docx` and the rough design memo in `SSI Data Analysis.pdf`. Where the rough memo mentions variables not present in the current instrument, this PAP follows the instrument that will actually generate the data.

## 2. Theory Overview and Research Questions

Existing work has devoted extensive attention to whether affective polarization contributes to democratic erosion, but has given comparatively little attention to the reverse possibility that elite backsliding itself deepens partisan hostility and thereby reinforces a self-reinforcing cycle between polarization and democratic decline. This project addresses that gap by focusing on how citizens update their attitudes after exposure to hypothetical backsliding by partisan elites.

The study asks three main questions:

1. Does democratic backsliding increase affective polarization?
2. Does democratic backsliding increase willingness to tolerate future backsliding?
3. Through what elite-framing mechanisms do any such effects emerge?

Operationally, those questions are addressed by asking whether exposure to partisan democratic backsliding changes:

1. hostility toward members of the opposing party; and
2. willingness to reward the hypothetical governor in a future re-election campaign.

The study also asks whether those effects vary depending on:

1. whether the backsliding is committed by the respondent's in-party or out-party; and
2. whether elites frame the action in policy, electoral, or democracy terms.

The study makes four linked contributions, consistent with the theory overview:

1. It examines whether democratic backsliding itself can generate greater affective polarization.
2. It evaluates how citizens react when antidemocratic behavior is communicated through partisan elite messaging.
3. It tests whether policy, electoral-retaliation, and democracy-protection frames operate as distinct mechanisms shaping citizens' responses.
4. It treats democratic backsliding as a dynamic process in which elite action can alter citizens' later attitudes, thereby strengthening the external validity of the design.

## 3. Experimental Design

Respondents first report demographic and partisan information, complete feeling thermometers toward Republicans and Democrats, and indicate which potential gubernatorial action they consider the greatest threat to democratic governance. The five possible actions are:

1. partisan redistricting;
2. restrictions on political rallies;
3. partisan control over investigations of opposing politicians;
4. prosecutions of journalists for unfavorable coverage; and
5. restructuring the state supreme court in the incumbent's favor.

Each respondent is then shown a vignette tied to the action they selected as most threatening. This respondent-specific matching is intended to maximize the potential treatment effect by exposing each respondent to the form of backsliding he or she finds most normatively objectionable. Within that action-specific vignette, respondents are assigned to one of seven cells:

1. neutral control;
2. in-party governor, policy frame;
3. in-party governor, electoral frame;
4. in-party governor, democracy frame;
5. out-party governor, policy frame;
6. out-party governor, electoral frame;
7. out-party governor, democracy frame.

Because the action-specific vignette is chosen before treatment assignment, analyses will control for the respondent-selected action using action fixed effects.

The rough theory overview describes the control as an apolitical topic. The current instrument operationalizes that control more narrowly as a neutral, non-backsliding vignette in the same issue domain. This is the specification used in the present PAP because it is the design that will actually generate the data.

## 4. Hypotheses

### H1: Backsliding versus control

Exposure to any backsliding vignette will:

1. increase affective polarization; and
2. increase willingness to support the hypothetical governor in a future re-election campaign, interpreted as greater tolerance for future backsliding.

### H2: In-party versus out-party backsliding

Backsliding by the respondent's in-party will generate greater tolerance for the governor than backsliding by the out-party.

### H3: Framing effects

Compared with policy framing, electoral-retaliation framing will most strongly increase tolerance for future backsliding and out-party hostility. Democracy-protection framing may either reduce or increase support, depending on whether respondents accept the democratic justification. These framing contrasts constitute the study's main mechanism test.

### H4: Exploratory moderation

Framing effects may differ when the governor is in-party rather than out-party. These interaction tests are substantively important but will be treated as exploratory unless sample size is large enough for precise inference.

## 5. Sample and Exclusion Rules

The primary analysis sample will include all respondents who:

1. are at least 18 years old;
2. complete the survey; and
3. are assigned to one of the experimental cells.

The following rules will be applied before estimation:

1. The Qualtrics metadata row containing `ImportId` values will be dropped.
2. Respondents with missing treatment assignment or missing selected-action data will be excluded.
3. Primary analyses will not exclude respondents based on attention or manipulation checks.
4. A secondary robustness sample will exclude respondents who fail the attention check.

## 6. Variable Construction

### 6.1 Primary outcomes

#### Outcome 1: Tolerance for future backsliding via re-election support

`Q-ReElection` is measured on a 1-7 scale from `Very unlikely` to `Very likely`. Higher values indicate greater willingness to vote for the governor for re-election. In the theory overview, this item is the study's operational measure of willingness to tolerate future backsliding, because support for the same politician after observing an antidemocratic act implies willingness to reward or excuse such behavior electorally.

#### Outcome 2: Affective polarization additive index

Three post-treatment items measure comfort with an out-party member as:

1. an in-law;
2. a close personal friend; and
3. a next-door neighbor.

Each item is measured on a 1-7 scale from `Very uncomfortable` to `Very comfortable`. The primary post-treatment affective-polarization measure will reverse-code these items and average them so that higher values indicate greater discomfort with the out-party and therefore greater affective polarization.

If a respondent answers at least two of the three items, the index will be computed as the mean of available items. If fewer than two items are observed, the index will be missing.

#### Outcome 3: Affective polarization latent score

As a secondary operationalization of the same post-treatment construct, I will estimate a one-factor latent score using the same three social-distance items. This latent score is intended to capture the common underlying dimension of out-party discomfort without requiring the post-treatment affective-polarization measure to be on the same scale as the pre-treatment feeling-thermometer measure.

The additive index is the primary confirmatory affective-polarization outcome. The latent score is a preregistered secondary outcome used to check robustness to outcome construction.

### 6.2 Pre-treatment covariates

#### Baseline affective polarization

The preregistered pre-treatment affective-polarization control will be based on the two feeling thermometer items:

- `republican_therm`: feeling thermometer toward Republicans;
- `democratic_therm`: feeling thermometer toward Democrats;
- `baseline_affpol_signed = republican_therm - democratic_therm`;
- `baseline_affpol_abs = |republican_therm - democratic_therm|`.

The main regression specification will use `baseline_affpol_abs` as the primary covariate because the updated design notes indicate that the magnitude of partisan affect, rather than its partisan direction, is the preferred preregistered control. I will still retain `baseline_affpol_signed` descriptively and in secondary analyses.

#### In-party and out-party thermometer controls

Using the respondent's constructed in-party (`InParty`) and out-party (`OutParty`) labels, I will also define:

- `inparty_feeling`: feeling thermometer rating toward the respondent's in-party; and
- `outparty_feeling`: feeling thermometer rating toward the respondent's out-party.

These variables will be used in separate supplementary model sets: one using `inparty_feeling` as the pre-treatment feeling control and one using `outparty_feeling` as the pre-treatment feeling control. This follows the updated note that these variables should each be analyzed in their own specifications.

#### Baseline democratic norm commitment

`Q-AffPolarization` asks how important it is that the government follows democratic rules and norms even if that means the respondent's party loses. Although the exported variable name is misleading, the item is substantively a pre-treatment democratic commitment measure. It will be coded 1-7 with higher values indicating stronger commitment to democratic norms.

#### Party identification scale

A seven-point party identification variable will be constructed:

1. Strong Democrat = -3
2. Weak Democrat = -2
3. Lean Democrat = -1
4. Pure independent / neither / no preference = 0
5. Lean Republican = +1
6. Weak Republican = +2
7. Strong Republican = +3

This covariate is included for precision and because the rough design memo explicitly anticipated a party-affiliation scale.

### 6.3 Treatment indicators

Primary treatment indicators are:

1. `treated_any`: 1 if `Treat_Party != "Control"`, 0 otherwise;
2. `inparty_treat`: 1 if `Treat_Party == "InParty"`, 0 if `Treat_Party == "OutParty"`; defined only in treated observations;
3. `frame_electoral`: 1 if `Treat_Frame == "Electoral"`;
4. `frame_democracy`: 1 if `Treat_Frame == "Democracy"`.

`Policy` is the omitted reference frame. In full-sample models, the control group is the omitted treatment category.

### 6.4 Action fixed effects

`Q-DemThreat` records the pre-treatment action the respondent selected as the greatest threat to democracy. Because assignment occurs after this choice, the analysis will include action fixed effects in all main regressions. The selected action will also be used in descriptive balance checks and exploratory heterogeneity analyses.

## 7. Estimands and Main Models

The primary estimation strategy is OLS with heteroskedasticity-robust HC2 standard errors. OLS is appropriate because:

1. the additive social-distance index is approximately continuous by construction;
2. the 1-7 re-election item is easily interpretable in linear probability-style mean differences;
3. OLS coefficients directly represent average treatment effects on the observed scale.

The main confirmatory outcomes are:

1. governor support (`Q-ReElection`); and
2. the additive affective-polarization index.

The latent affective-polarization score will be estimated in parallel as a preregistered secondary operationalization. Ordered logit models for `Q-ReElection` will be reported as robustness checks only.

### 7.1 Research Question 1: Any backsliding versus control

For each outcome \(Y_i\),

\[
Y_i = \alpha + \beta_1 TreatedAny_i + \beta_2 |APPre_i| + \beta_3 DemNormsPre_i + \beta_4 PID7_i + \delta_{a(i)} + \varepsilon_i
\]

where \(\delta_{a(i)}\) denotes fixed effects for the respondent-selected action.

Interpretation:

- `β1` is the intent-to-treat (ITT) effect of exposure to any backsliding vignette relative to the neutral control.

### 7.2 Research Question 2: In-party versus out-party backsliding

Estimated on treated observations only:

\[
Y_i = \alpha + \beta_1 InPartyTreat_i + \beta_2 |APPre_i| + \beta_3 DemNormsPre_i + \beta_4 PID7_i + \delta_{a(i)} + \varepsilon_i
\]

Interpretation:

- `β1` measures how much more supportive or hostile respondents become when the backsliding is committed by the in-party rather than the out-party.

### 7.3 Research Question 3: Framing effects

Estimated on treated observations only:

\[
Y_i = \alpha + \beta_1 Electoral_i + \beta_2 Democracy_i + \beta_3 InPartyTreat_i + \beta_4 |APPre_i| + \beta_5 DemNormsPre_i + \beta_6 PID7_i + \delta_{a(i)} + \varepsilon_i
\]

Interpretation:

1. `β1` compares electoral framing with policy framing.
2. `β2` compares democracy framing with policy framing.
3. A post-estimation Wald test will compare electoral framing with democracy framing.

### 7.4 Research Question 4: Framing by party interaction

Estimated on treated observations only:

\[
Y_i = \alpha + \beta_1 Electoral_i + \beta_2 Democracy_i + \beta_3 InPartyTreat_i + \beta_4 (Electoral_i \times InPartyTreat_i) + \beta_5 (Democracy_i \times InPartyTreat_i) + \beta_6 |APPre_i| + \beta_7 DemNormsPre_i + \beta_8 PID7_i + \delta_{a(i)} + \varepsilon_i
\]

Interpretation:

1. `β4` asks whether the electoral frame works differently when the governor is in-party rather than out-party.
2. `β5` asks whether the democracy frame works differently when the governor is in-party rather than out-party.

These interaction models will be labeled exploratory in the final paper unless precision is high.

### 7.5 Separate control-set models

In addition to the main specifications above, I will estimate two preregistered supplementary control sets:

1. replace `|APPre|` with `inparty_feeling`; and
2. replace `|APPre|` with `outparty_feeling`.

These models address the updated note that pre-treatment feelings toward the respondent's in-party and out-party should each be analyzed separately, rather than only through a single difference score.

## 8. Inference Rules

All confirmatory hypothesis tests will be two-sided with \(\alpha = 0.05\). I will report:

1. point estimates;
2. HC2 robust standard errors;
3. 95% confidence intervals; and
4. raw and adjusted p-values.

To account for multiple testing:

1. For Research Questions 1 and 2, I will Holm-adjust the p-values across the two primary outcomes: governor support and the additive affective-polarization index.
2. For Research Question 3, I will Holm-adjust the four confirmatory frame contrasts across those same two primary outcomes.
3. The latent affective-polarization outcome, interaction models, and separate control-set models will be reported separately and clearly labeled as secondary or exploratory.

## 9. Balance, Manipulation Checks, and Descriptives

### 9.1 Balance tests

Before estimating treatment effects, I will test balance across the seven experimental cells on pre-treatment characteristics:

1. age;
2. gender;
3. race;
4. party affiliation / party identification;
5. baseline affective polarization magnitude;
6. baseline democratic norm commitment; and
7. selected action (`Q-DemThreat`).

For categorical variables, I will use chi-square tests. For numeric variables, I will use omnibus F-tests from regressions on condition indicators.

In addition to formal tests, I will produce descriptive balance tables showing category shares by treatment group and flag any category where the spread across treatment groups exceeds roughly 10 percentage points, with especially close scrutiny for spreads above 20 percentage points. This incorporates the updated instruction to check whether demographic compositions remain within a 10-20% range across treatment groups.

### 9.2 Manipulation checks

Two checks will be summarized descriptively:

1. attention to whether the governor was Republican, Democrat, or unspecified;
2. whether respondents recognized the intended frame as electoral, policy, or democracy-related.

Manipulation checks will not be used as exclusion criteria in the primary ITT analyses. They will be used only for descriptive diagnosis and secondary robustness checks.

## 10. Missing Data

The main analyses will use complete-case estimation at the model level. I will not impute missing outcomes or missing covariates in the primary analysis. The number of observations used in each model will be reported explicitly.

## 11. Exploratory Analyses

The following analyses are exploratory:

1. heterogeneous treatment effects by selected action;
2. heterogeneous treatment effects by baseline democratic norm commitment;
3. heterogeneous treatment effects by party identification strength;
4. models using the signed thermometer difference instead of the absolute difference;
5. ordered logit robustness models for governor support.

## 12. Planned Tables and Figures

### Tables

1. Descriptive statistics and sample sizes by condition.
2. Balance test table for pre-treatment covariates.
3. Main ITT estimates: any backsliding versus control.
4. Treated-sample estimates: in-party versus out-party.
5. Treated-sample framing estimates and interaction models.
6. Separate control-set models using in-party and out-party thermometer controls.
7. Manipulation-check rates by treatment condition.

### Figures

1. Distribution of selected democratic threats in the sample.
2. Mean governor-support outcome by experimental condition with 95% confidence intervals.
3. Mean additive affective-polarization index by experimental condition with 95% confidence intervals.
4. Mean latent affective-polarization score by experimental condition with 95% confidence intervals.
5. Coefficient plot for main treatment and framing estimates.

## 13. Implementation

The accompanying Python script will:

1. clean the Qualtrics CSV export;
2. construct all variables described above;
3. run balance tests;
4. estimate the main OLS models using the absolute thermometer difference as the primary preregistered control;
5. estimate parallel secondary models using additive and latent affective-polarization outcomes and separate in-party / out-party feeling controls;
6. run ordered-logit robustness checks for governor support;
7. export tidy regression tables; and
8. generate the planned descriptive and coefficient figures.

## 14. Note on Deviations from the Rough Memo

The rough memo proposed post-treatment affective-polarization measures based on repeated feeling thermometers and mentioned a pre-treatment tolerance-for-backsliding covariate. The updated memo clarifies that preregistration should instead:

1. define baseline affective polarization as the difference between the Republican and Democratic feeling thermometers, using the absolute value as the main control variable;
2. retain separate in-party and out-party feeling-thermometer control specifications;
3. use the democratic-norms item as the pre-treatment democratic-attitudes covariate; and
4. estimate post-treatment affective polarization in two ways: an additive index and a latent-variable score based on the three social-distance items.

This adjustment keeps the analysis aligned with the survey that will actually be fielded.
