# Analysis Pipeline: UK Ash User Survey

**Paper:** "Where Do Users Go When a Purpose-Built AI Wellbeing Tool Is Removed? Evidence From a Natural Experiment in the UK"

**Authors:** Caitlin Stamatis, PhD, et al. (Slingshot AI)

---

## Overview

This folder contains the complete, replicable analysis pipeline for the UK Ash user survey (N = 393). The analysis produces all quantitative results, qualitative coding, tables, and figures reported in the manuscript.

## Directory Structure

```
UK survey/
├── data/
│   ├── UK survey_Submissions_2026-03-16.csv    # Raw survey export (Tally)
│   └── UK survey items overview.pdf             # Survey instrument screenshot
├── background/
│   ├── UK Perspective Piece.docx                # Prior unpublished perspective piece
│   ├── MHRA context.docx                        # MHRA engagement timeline summary
│   └── Slingshot AI UK Mental Health Goals.pdf   # Regulatory context slides
├── analysis/                                     # ← YOU ARE HERE
│   ├── README.md                                 # This file
│   ├── 01_quantitative_analysis.py               # Descriptive statistics
│   ├── 02_qualitative_coding.py                  # Free-text theme coding
│   ├── 03_figures.py                             # Figures 1–3
│   └── 04_tables.py                              # Tables 1–3 (as CSV)
├── results/                                      # Generated outputs (created by scripts)
│   ├── quantitative_summary.txt
│   ├── coded_responses.csv
│   ├── qualitative_summary.txt
│   ├── fig1_primary_source.png
│   ├── fig2_access_change.png
│   ├── fig3_why_ai.png
│   ├── table1_sample.csv
│   ├── table2_sources.csv
│   └── table3_ai_use.csv
└── UK_Survey_Paper_FULL_DRAFT.docx               # Manuscript draft
```

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib

Install dependencies:

```bash
pip install pandas numpy matplotlib
```

## How to Run

From the `analysis/` directory, run all four scripts in order:

```bash
cd "UK survey/analysis"

# Step 1: Quantitative descriptive statistics
python 01_quantitative_analysis.py

# Step 2: Qualitative coding of free-text responses
python 02_qualitative_coding.py

# Step 3: Generate publication figures
python 03_figures.py

# Step 4: Generate tables as CSV
python 04_tables.py
```

Or run everything at once:

```bash
python 01_quantitative_analysis.py && \
python 02_qualitative_coding.py && \
python 03_figures.py && \
python 04_tables.py
```

All outputs are saved to `../results/`.

---

## Script Details

### 01_quantitative_analysis.py

Produces all descriptive statistics reported in the paper:

1. **Sample characteristics** — N, completion rate, response rate, age distribution, UK region distribution
2. **Where users turned** (multi-select Q1) — counts and percentages for each checkbox option
3. **Primary source of support** (single-select Q2) — with free-text "Other" responses classified into standard categories
4. **AI use frequency** (Q3) — distribution among all respondents and among AI users specifically
5. **AI role in life** (Q4) — how AI fits into daily support patterns
6. **AI use cases** (Q5, multi-select) — what users use GPAI for
7. **Motivations for AI** (Q6, multi-select) — why users chose GPAI
8. **Access change** (Q7) — perceived change since Ash removed, including no-support subgroup breakdown
9. **Wellbeing** (Q8) — self-reported wellbeing over past month
10. **Return to Ash** (Q9) — likelihood of returning if available

**Key methodological notes:**
- Column names in the CSV contain Unicode characters (curly apostrophes, em dashes). All column lookups use keyword-matching (`find_col()`) rather than exact string matching to handle this robustly.
- Boolean checkbox columns are stored as Python `True/False` (not string `'true'/'false'`). The script uses `.sum()` directly on boolean columns.
- Free-text "Other" responses in the primary source question are reclassified into standard categories via `classify_primary()`.

**Output:** `results/quantitative_summary.txt`

### 02_qualitative_coding.py

Implements hybrid inductive-deductive thematic analysis of free-text responses to Q9 ("Is there anything you're using now that works better—or worse—than Ash did for you?").

**Coding approach:**
- AI-assisted keyword-pattern matching using regular expressions
- 15 non-mutually-exclusive thematic codes across 6 domains
- Patterns were developed inductively by reading responses, then iteratively refined across three coding passes to improve recall
- Responses can receive multiple codes (mean ~1.7 codes/response)
- 24 manual overrides applied after lead author review
- Uncoded responses: 2 of 272 (0.7%)

**Codebook (15 codes, 6 domains):**

| Domain | Code | Description |
|--------|------|-------------|
| GPAI Experience | T1_GPAI_INFERIOR | GPAI described as worse than Ash |
| | T2_GPAI_ADEQUATE | GPAI described as acceptable substitute |
| Support Gap | T3_NO_REPLACEMENT_FOUND | No adequate replacement found |
| | T4_NHS_ACCESS_BARRIER | NHS services inaccessible (waiting times, etc.) |
| | T5_HUMAN_PREFERRED_INACCESSIBLE | Wants human support but can't access it |
| | T6_HUMAN_ACCESSED | Currently seeing a therapist or professional |
| What Ash Provided | T7_MEMORY_CONTINUITY | Valued Ash's memory / personalisation |
| | T8_INSIGHTS_REFLECTIONS | Ash helped with self-awareness / growth |
| | T9_AVAILABILITY_24_7 | Valued always-on availability |
| | T10_PRIVACY_TRUST_SAFETY | Valued non-judgmental / private space |
| Distress / Loss | T11_DISTRESS_AT_LOSS | Emotional distress at losing Ash |
| Workarounds | T12_VPN_WORKAROUND | Using VPN to continue accessing Ash |
| | T14_OTHER_WELLBEING_APP | Switched to another wellbeing app |
| | T15_SELF_MANAGE_INFORMAL | Self-managing via journaling, exercise, etc. |
| Ash Critique | T13_ASH_CRITIQUE | Criticism or suggested improvements for Ash |

**Methodological disclosure:** The coding was AI-assisted (patterns developed with the help of Claude). This is disclosed transparently in the Methods section. All coded responses should be reviewed by the lead author for face-validity.

**Outputs:**
- `results/coded_responses.csv` — one row per response, with `orig_idx`, `text`, and `codes_str`
- `results/qualitative_summary.txt` — frequency counts per code and domain

### 03_figures.py

Generates three publication-quality figures (300 DPI PNG):

- **Figure 1:** Horizontal bar chart showing primary source of support. Highlights GPAI (blue) and "haven't sought support" (red) with bracket annotation showing the combined 51%.
- **Figure 2:** Two-panel horizontal bar chart comparing access-change distributions: (A) all respondents, (B) "haven't sought support" subgroup. Green-to-red colour gradient.
- **Figure 3:** Horizontal bar chart showing motivations for choosing GPAI, among AI users only.

**Outputs:** `results/fig1_primary_source.png`, `results/fig2_access_change.png`, `results/fig3_why_ai.png`

### 04_tables.py

Generates CSV versions of the three tables in the paper:

- **Table 1:** Sample characteristics (age range, UK region) with n and %
- **Table 2:** Sources of support — both multi-select (Q1) and primary (Q2) columns side-by-side
- **Table 3:** AI use patterns among GPAI users — frequency, role, use cases, motivations

**Outputs:** `results/table1_sample.csv`, `results/table2_sources.csv`, `results/table3_ai_use.csv`

---

## Data Notes

### Raw data format
- **Source:** Tally survey platform export
- **File:** `UK survey_Submissions_2026-03-16.csv`
- **Rows:** 393 (one per respondent)
- **Columns:** 45
  - Cols 0–4: metadata (submission ID, respondent ID, timestamps, email)
  - Cols 5: multi-select summary (text, not used in analysis)
  - Cols 6–16: individual checkbox booleans for Q1 (where turned for support)
  - Col 17: Q2 single-select primary source (free-text if "Other")
  - Col 18: Q3 AI use frequency
  - Col 19: Q4 AI role in life
  - Cols 20–28: Q5 use case checkboxes
  - Cols 29–38: Q6 motivation checkboxes
  - Col 39: Q7 access change (5-point Likert)
  - Col 40: Q8 return to Ash (Likert)
  - Col 41: Q9 wellbeing (Likert)
  - Col 42: Q10 free-text (qualitative)
  - Cols 43–44: demographics (age range, UK region)

### Known data issues
- ~30 respondents have 5+ blank substantive fields (likely mid-survey dropout). These are included in analyses where they provided data; they are not excluded wholesale.
- Response rate denominator (1,178 eligible users) should be verified by the research team.
- The 393 vs. 363 "completed all items" discrepancy is due to ~30 partial completions.

### Encoding
- CSV uses UTF-8 with BOM (`\ufeff` at start)
- Column names contain curly/smart apostrophes (Unicode) — all scripts use keyword matching to handle this

---

## Key Findings (for reference)

| Finding | Value |
|---------|-------|
| N (total respondents) | 393 |
| Response rate | 5.3% (393 / 7,415) |
| GPAI as primary source | 27% (104 / 384) |
| Haven't sought support as primary | 26% (100 / 384) |
| Combined: GPAI + no support | 53% (204 / 384) |
| Professional support as primary | 13% (50 / 384) |
| Any AI use | 77% (303 / 393) |
| Weekly+ AI use | 49% (184 / 374) |
| Worse access to support | 60% (219 / 364) |
| Would return to Ash | 89% (325 / 364) |

---

## Reproducibility Notes

1. All scripts use relative paths from the `analysis/` directory.
2. Column lookups use keyword matching (`find_col()`) to handle Unicode variability in column names.
3. The qualitative coding (Script 02) is deterministic — no randomness involved. Rerunning will produce identical results.
4. Figure styling uses matplotlib defaults with minimal customisation; minor rendering differences may occur across matplotlib versions.
5. The `classify_primary()` function in Scripts 01, 03, and 04 contains the same categorisation logic — this is intentionally duplicated (rather than imported) so each script is self-contained and can run independently.

---

## Data Availability

The survey data are not publicly available due to the inclusion of personally identifiable information. De-identified data may be made available upon reasonable request to the corresponding author.

---

## Citation

If using this pipeline, please cite the associated paper:

> Stamatis, C.A., Kruzan, K.P., Hsu, J., Ungless, M.A., & Hull, T.D. (2026). Generic AI or Nothing: Support-Seeking Patterns After Market Withdrawal of a Purpose-Built AI Wellbeing Tool. [Journal TBD].
