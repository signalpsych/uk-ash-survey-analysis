"""
01_quantitative_analysis.py
===========================
Quantitative analysis of the UK Ash user survey (N=393).
Produces all descriptive statistics reported in the paper, printed to stdout
and saved to results/quantitative_summary.txt.

Usage:
    python 01_quantitative_analysis.py

Input:  ../data/UK survey_Submissions_2026-03-16.csv
Output: ../results/quantitative_summary.txt
"""

import os, sys
import pandas as pd
import numpy as np
from collections import OrderedDict

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(SCRIPT_DIR, "..", "data",
                          "UK survey_Submissions_2026-03-16.csv")
OUT_DIR    = os.path.join(SCRIPT_DIR, "..", "results")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH   = os.path.join(OUT_DIR, "quantitative_summary.txt")

# ── Helper: find column by keyword ───────────────────────────────────────────
def find_col(df, *keywords):
    """Return the first column whose name contains ALL keywords (case-insensitive)."""
    for c in df.columns:
        cl = c.lower()
        if all(k.lower() in cl for k in keywords):
            return c
    raise KeyError(f"No column found matching keywords: {keywords}")

def find_cols(df, *keywords):
    """Return ALL columns whose names contain ALL keywords (case-insensitive)."""
    return [c for c in df.columns if all(k.lower() in c.lower() for k in keywords)]

# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
N = len(df)

# Buffer to collect all printed output
output_lines = []
def printb(*args, **kwargs):
    """Print to stdout and buffer."""
    import io
    buf = io.StringIO()
    print(*args, file=buf, **kwargs)
    text = buf.getvalue()
    sys.stdout.write(text)
    output_lines.append(text)

# ══════════════════════════════════════════════════════════════════════════════
# 1. SAMPLE CHARACTERISTICS
# ══════════════════════════════════════════════════════════════════════════════
printb("=" * 70)
printb("1. SAMPLE CHARACTERISTICS")
printb("=" * 70)
printb(f"Total respondents (N): {N}")

# Completion: count rows with ≤5 blank substantive fields (cols 5–44)
substantive = df.iloc[:, 5:]
blank_counts = substantive.isnull().sum(axis=1)
complete = (blank_counts <= 5).sum()
printb(f"Completed all items (≤5 blanks): {complete} ({complete/N*100:.1f}%)")
printb(f"Response rate: 393 / 1,178 eligible = {393/1178*100:.1f}%")

# Age
age_col = find_col(df, "age")
n_age = df[age_col].notna().sum()
printb(f"\nAge distribution (n={n_age}):")
age_vc = df[age_col].value_counts().sort_index()
for val, cnt in age_vc.items():
    printb(f"  {val}: {cnt} ({cnt/n_age*100:.1f}%)")

# Region
region_col = find_col(df, "region")
n_region = df[region_col].notna().sum()
printb(f"\nUK region distribution (n={n_region}):")
region_vc = df[region_col].value_counts()
for val, cnt in region_vc.items():
    printb(f"  {val}: {cnt} ({cnt/n_region*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 2. WHERE USERS TURNED (multi-select, Q1 checkbox columns)
# ══════════════════════════════════════════════════════════════════════════════
printb("\n" + "=" * 70)
printb("2. WHERE USERS TURNED FOR SUPPORT (multi-select)")
printb("=" * 70)

# Checkbox columns are cols 6–16
checkbox_cols = df.columns[6:17]
labels = {
    "general-purpose ai":    "General-purpose AI (GPAI)",
    "private therapist":     "Private therapist / counsellor",
    "friends, family":       "Friends, family, or partner",
    "support groups":        "Support groups or community groups",
    "workplace":             "Workplace support / EAP",
    "online forums":         "Online forums or social media",
    "books, podcasts":       "Books, podcasts, or self-help",
    "haven't sought":        "Haven't sought support",
    "other mental health":   "Other wellbeing apps",
    "nhs services":          "NHS services",
}

printb(f"{'Source':<45} {'n':>5} {'%':>7}")
printb("-" * 60)
for col in checkbox_cols:
    # Values are Python booleans (True/False) after pandas reads CSV
    n = df[col].sum() if df[col].dtype == bool else (df[col] == True).sum()
    short = col.split("(")[-1].rstrip(")") if "(" in col else col.split("?")[-1].strip()
    # Truncate for display
    label = short[:43]
    n_valid = df[col].notna().sum()
    printb(f"  {label:<43} {n:>5} {n/n_valid*100:>6.1f}%")

# ══════════════════════════════════════════════════════════════════════════════
# 3. PRIMARY SOURCE (single-select, Q2)
# ══════════════════════════════════════════════════════════════════════════════
printb("\n" + "=" * 70)
printb("3. PRIMARY SOURCE OF SUPPORT (single-select)")
printb("=" * 70)

primary_col = find_col(df, "which one", "relied")
primary = df[primary_col].dropna()
printb(f"Respondents answering: {len(primary)}")

# Map free-text "Other" responses into categories for cleaner counts
def classify_primary(val):
    v = str(val).lower().replace("\u2019", "'")  # normalize curly apostrophes
    if "general-purpose ai" in v or "chatgpt" in v:
        return "General-purpose AI"
    if "haven't sought" in v or "struggling alone" in v:
        return "Haven't sought support"
    if "friends" in v or "family" in v or "partner" in v:
        return "Friends, family, or partner"
    if "private therapist" in v or "counsell" in v:
        return "Private therapist / counsellor"
    if "nhs" in v:
        return "NHS services"
    if "other mental health" in v or "wellbeing app" in v:
        return "Other wellbeing apps"
    if "books" in v or "podcasts" in v or "self-help" in v:
        return "Books, podcasts, or self-help"
    if "support group" in v or "community" in v:
        return "Support groups"
    if "online forum" in v or "social media" in v:
        return "Online forums / social media"
    if "workplace" in v or "eap" in v:
        return "Workplace / EAP"
    if "vpn" in v or "still us" in v and "ash" in v:
        return "Ash (via VPN)"
    return "Other"

primary_mapped = primary.map(classify_primary)
primary_vc = primary_mapped.value_counts()
printb(f"\n{'Primary source':<40} {'n':>5} {'%':>7}")
printb("-" * 55)
for val, cnt in primary_vc.items():
    printb(f"  {val:<38} {cnt:>5} {cnt/len(primary)*100:>6.1f}%")

# Key combined statistic
gpai_n = primary_vc.get("General-purpose AI", 0)
nosup_n = primary_vc.get("Haven't sought support", 0)
combined = gpai_n + nosup_n
printb(f"\nCombined GPAI + no support: {combined} ({combined/len(primary)*100:.1f}%)")
prof_n = primary_vc.get("Private therapist / counsellor", 0) + primary_vc.get("NHS services", 0)
printb(f"Professional support (therapist + NHS): {prof_n} ({prof_n/len(primary)*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 4. AI USE FREQUENCY & ROLE (among AI users)
# ══════════════════════════════════════════════════════════════════════════════
printb("\n" + "=" * 70)
printb("4. GENERAL-PURPOSE AI USE PATTERNS")
printb("=" * 70)

freq_col = find_col(df, "how often", "general-purpose ai")
freq = df[freq_col].dropna()
printb(f"Respondents answering frequency Q: {len(freq)}")
freq_vc = freq.value_counts()
for val, cnt in freq_vc.items():
    printb(f"  {val}: {cnt} ({cnt/len(freq)*100:.1f}%)")

# Weekly+ users
weekly_labels = [v for v in freq_vc.index if "daily" in v.lower() or "week" in v.lower()]
weekly_n = sum(freq_vc[v] for v in weekly_labels)
printb(f"\nWeekly+ users: {weekly_n} ({weekly_n/len(freq)*100:.1f}% of those who answered)")

# Exclude "I don't use..." to get AI-user subset
ai_users = freq[~freq.str.contains("don't use|do not use|never", case=False, na=False)]
printb(f"AI users (any frequency): {len(ai_users)} ({len(ai_users)/N*100:.1f}% of N)")

# Role in life
role_col = find_col(df, "fit into your life")
role = df[role_col].dropna()
printb(f"\nRole of AI (n={len(role)}):")
role_vc = role.value_counts()
for val, cnt in role_vc.items():
    printb(f"  {val}: {cnt} ({cnt/len(role)*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 5. AI USE CASES (multi-select, Q4 checkboxes)
# ══════════════════════════════════════════════════════════════════════════════
printb("\n" + "=" * 70)
printb("5. AI USE CASES (multi-select, among AI users)")
printb("=" * 70)

usecase_cols = find_cols(df, "mainly use general-purpose ai for", "(")
# Filter to AI users only
gpai_check_col = find_col(df, "general-purpose ai tools (e.g.")
ai_mask = df[gpai_check_col] == True
n_ai = ai_mask.sum()
printb(f"AI users (checked GPAI in Q1): {n_ai}")

for col in usecase_cols:
    label = col.split("(")[-1].rstrip(")")
    n = df.loc[ai_mask, col].sum() if df[col].dtype == bool else (df.loc[ai_mask, col] == True).sum()
    printb(f"  {label:<45} {n:>4} ({n/n_ai*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 6. MOTIVATIONS FOR AI USE (multi-select, Q5 checkboxes)
# ══════════════════════════════════════════════════════════════════════════════
printb("\n" + "=" * 70)
printb("6. MOTIVATIONS FOR CHOOSING AI (multi-select, among AI users)")
printb("=" * 70)

motiv_cols = find_cols(df, "why did you choose", "(")
for col in motiv_cols:
    label = col.split("(")[-1].rstrip(")").strip()
    n = df.loc[ai_mask, col].sum() if df[col].dtype == bool else (df.loc[ai_mask, col] == True).sum()
    printb(f"  {label:<45} {n:>4} ({n/n_ai*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 7. ACCESS CHANGE (Q6)
# ══════════════════════════════════════════════════════════════════════════════
printb("\n" + "=" * 70)
printb("7. ACCESS TO SUPPORT CHANGE")
printb("=" * 70)

access_col = find_col(df, "access to support changed")
access = df[access_col].dropna()
printb(f"Respondents: {len(access)}")
access_vc = access.value_counts()
for val, cnt in access_vc.items():
    printb(f"  {val}: {cnt} ({cnt/len(access)*100:.1f}%)")

worse = sum(access_vc.get(k, 0) for k in access_vc.index if "worse" in k.lower())
printb(f"\nTotal worse: {worse} ({worse/len(access)*100:.1f}%)")

# Subgroup: "haven't sought support" primary
nosup_mask = primary_mapped == "Haven't sought support"
nosup_idx = primary[nosup_mask].index
access_nosup = df.loc[nosup_idx, access_col].dropna()
printb(f"\nNo-support subgroup (n={len(access_nosup)}):")
access_nosup_vc = access_nosup.value_counts()
for val, cnt in access_nosup_vc.items():
    printb(f"  {val}: {cnt} ({cnt/len(access_nosup)*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 8. WELLBEING (Q8)
# ══════════════════════════════════════════════════════════════════════════════
printb("\n" + "=" * 70)
printb("8. GENERAL WELLBEING (past month)")
printb("=" * 70)

well_col = find_col(df, "general wellbeing")
well = df[well_col].dropna()
printb(f"Respondents: {len(well)}")
well_vc = well.value_counts()
for val, cnt in well_vc.items():
    printb(f"  {val}: {cnt} ({cnt/len(well)*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 9. RETURN TO ASH (Q7)
# ══════════════════════════════════════════════════════════════════════════════
printb("\n" + "=" * 70)
printb("9. LIKELIHOOD OF RETURNING TO ASH")
printb("=" * 70)

return_col = find_col(df, "likely", "use it again")
ret = df[return_col].dropna()
printb(f"Respondents: {len(ret)}")
ret_vc = ret.value_counts()
for val, cnt in ret_vc.items():
    printb(f"  {val}: {cnt} ({cnt/len(ret)*100:.1f}%)")

likely = sum(ret_vc.get(k, 0) for k in ret_vc.index if "likely" in k.lower() and "unlikely" not in k.lower())
printb(f"\nLikely to return (any 'likely'): {likely} ({likely/len(ret)*100:.1f}%)")

# ── Save ─────────────────────────────────────────────────────────────────────
with open(OUT_PATH, "w") as f:
    f.writelines(output_lines)
printb(f"\n✓ Summary saved to {OUT_PATH}")
