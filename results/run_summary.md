# Run Summary

- Analysis sample size: 97
- Treated observations: 76
- Control observations: 21
- Primary pre-treatment affective-polarization control: `baseline_affpol_abs` = |Republican thermometer - Democratic thermometer|
- Mean attention-check pass rate: 0.196
- Mean manipulation-check pass rate among treated: 0.276

## Balance tests

- Q-Age: chi_square statistic=51.766, p=0.144, n=97
- Q-Gender: chi_square statistic=26.764, p=0.084, n=97
- Q-Race: chi_square statistic=27.781, p=0.582, n=97
- Q-PartyAffiliation: chi_square statistic=29.138, p=0.215, n=97
- party_id_7pt: omnibus_f_test statistic=0.889, p=0.507, n=97
- baseline_affpol_abs: omnibus_f_test statistic=1.885, p=0.092, n=97
- baseline_demnorms: omnibus_f_test statistic=2.212, p=0.049, n=97
- selected_action: chi_square statistic=17.510, p=0.826, n=97

## Descriptive balance spread flags

- Category cells with more than a 10 percentage-point spread across treatment groups: 23
- Category cells with more than a 20 percentage-point spread across treatment groups: 16

## Key confirmatory estimates

- rq1_any_treatment | Tolerance for future backsliding (re-election support) | Any treatment vs control: b=-0.060, 95% CI [-1.232, 1.112], p=0.920, Holm p=1.000
- rq2_inparty_vs_outparty | Tolerance for future backsliding (re-election support) | In-party vs out-party: b=0.511, 95% CI [-0.399, 1.422], p=0.271, Holm p=0.271
- rq3_frame_effects | Tolerance for future backsliding (re-election support) | Electoral vs policy: b=-0.537, 95% CI [-1.564, 0.489], p=0.305, Holm p=0.915
- rq3_frame_effects | Tolerance for future backsliding (re-election support) | Democracy vs policy: b=0.081, 95% CI [-1.183, 1.345], p=0.900, Holm p=0.915
- rq1_any_treatment | Affective polarization (index) | Any treatment vs control: b=0.034, 95% CI [-0.477, 0.545], p=0.897, Holm p=1.000
- rq2_inparty_vs_outparty | Affective polarization (index) | In-party vs out-party: b=-0.328, 95% CI [-0.739, 0.082], p=0.117, Holm p=0.234
- rq3_frame_effects | Affective polarization (index) | Electoral vs policy: b=-0.239, 95% CI [-0.736, 0.258], p=0.345, Holm p=0.915
- rq3_frame_effects | Affective polarization (index) | Democracy vs policy: b=-0.560, 95% CI [-1.086, -0.035], p=0.036, Holm p=0.146

## Latent outcome estimates

- rq1_any_treatment | Any treatment vs control: b=-0.054, 95% CI [-0.512, 0.404], p=0.816
- rq2_inparty_vs_outparty | In-party vs out-party: b=0.100, 95% CI [-0.403, 0.603], p=0.698
- rq3_frame_effects | Electoral vs policy: b=-0.219, 95% CI [-0.814, 0.376], p=0.471
- rq3_frame_effects | Democracy vs policy: b=0.137, 95% CI [-0.527, 0.801], p=0.686
- rq4_frame_x_party | Electoral frame x in-party: b=0.157, 95% CI [-1.155, 1.468], p=0.815
- rq4_frame_x_party | Democracy frame x in-party: b=-0.402, 95% CI [-1.777, 0.974], p=0.567

## Sensitivity control sets

- Separate models also estimated with `inparty_feeling` as the pre-treatment feeling-thermometer control.
- Separate models also estimated with `outparty_feeling` as the pre-treatment feeling-thermometer control.