# UK Ash survey analysis

Analysis code for:

> Stamatis CA, Kruzan KP, Hsu J, Ungless MA, Hull TD. Support-Seeking After Market Withdrawal of a Purpose-Built AI Wellbeing Tool (Ash): Cross-Sectional Survey.

## Contents

| Script | Output |
|---|---|
| `01_quantitative_analysis.py` | descriptive statistics (`results/quantitative_summary.txt`) |
| `02_qualitative_coding.py` | free-text coding (`results/coded_responses.csv`, `results/qualitative_summary.txt`) |
| `03_figures.py` | Figures 1-4 (`results/*.png`) |
| `04_tables.py` | Tables 1-3 (`results/table*.csv`) |

Scripts expect the raw survey export at `data/UK survey_Submissions_2026-03-16.csv` and write to `results/`. Run in order; `03` and `04` depend on `02`'s output.

## Qualitative coding

The codebook (15 codes across five domains) is defined in `02_qualitative_coding.py` as regex pattern lists, applied deterministically to all analyzable responses. Manual reclassifications, reviewed by the first author, are listed in `MANUAL_OVERRIDES` with row indices and brief content notes. Code definitions, decision rules, and anchor examples are in Multimedia Appendix 3 of the paper. Re-running the script reproduces the published coding exactly.

## Data

Survey responses are not included in this repository. De-identified response-level data are available from the corresponding author on reasonable request.

## Requirements

Python ≥3.10 with `pandas`, `numpy`, and `matplotlib`.
