"""Tables 1-3 as CSVs (sample characteristics, support sources, AI use
patterns). Writes to results/.
"""

import os
import pandas as pd
import numpy as np

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(SCRIPT_DIR, "..", "data",
                          "UK survey_Submissions_2026-03-16.csv")
OUT_DIR    = os.path.join(SCRIPT_DIR, "..", "results")
os.makedirs(OUT_DIR, exist_ok=True)

# Helper
def find_col(df, *keywords):
    for c in df.columns:
        cl = c.lower()
        if all(k.lower() in cl for k in keywords):
            return c
    raise KeyError(f"No column found matching keywords: {keywords}")

# Load data
df = pd.read_csv(DATA_PATH)
N = len(df)

# TABLE 1: Sample characteristics

age_col = find_col(df, "age")
region_col = find_col(df, "region")

n_age = df[age_col].notna().sum()

n_region = df[region_col].notna().sum()

rows = []
# Age
age_vc = df[age_col].value_counts().sort_index()
for val, cnt in age_vc.items():
    rows.append({"Category": "Age", "Value": val, "n": cnt, "%": round(cnt/n_age*100, 1)})

# Region
region_vc = df[region_col].value_counts()
for val, cnt in region_vc.items():
    rows.append({"Category": "Region", "Value": val, "n": cnt, "%": round(cnt/n_region*100, 1)})

table1 = pd.DataFrame(rows)
table1.to_csv(os.path.join(OUT_DIR, "table1_sample.csv"), index=False)
print(f"Table 1 saved ({len(table1)} rows)")

# TABLE 2: Sources of support

# Multi-select columns (cols 6-16)
checkbox_cols = df.columns[6:17]
source_labels = {
    6:  "General-purpose AI (e.g. ChatGPT)",
    7:  "Private therapist / counsellor",
    8:  "Friends, family, or partner",
    9:  "Support groups / community groups",
    10: "Workplace support / EAP",
    11: "Online forums / social media",
    12: "Books, podcasts, or self-help",
    13: "Haven't sought support",
    14: "Other",
    15: "Other wellbeing apps",
    16: "NHS services",
}

# Primary source classification
primary_col = find_col(df, "which one", "relied")
primary = df[primary_col].dropna()

def classify_primary(val):
    v = str(val).lower().replace("\u2019", "'")  # normalize curly apostrophes
    if "general-purpose ai" in v or "chatgpt" in v:
        return "General-purpose AI (e.g. ChatGPT)"
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
        return "Support groups / community groups"
    if "online forum" in v or "social media" in v:
        return "Online forums / social media"
    if "workplace" in v or "eap" in v:
        return "Workplace support / EAP"
    if "vpn" in v or ("still us" in v and "ash" in v):
        return "Ash (via VPN)"
    return "Other"

primary_mapped = primary.map(classify_primary)
primary_vc = primary_mapped.value_counts()
total_primary = len(primary)

rows2 = []
for idx, col in enumerate(checkbox_cols):
    label = source_labels.get(idx + 6, col)
    n_valid = df[col].notna().sum()
    multi_n = df[col].sum() if df[col].dtype == bool else (df[col] == True).sum()
    prim_n = primary_vc.get(label, 0)
    rows2.append({
        "Source": label,
        "Multi-select n": int(multi_n),
        "Multi-select %": round(multi_n / n_valid * 100, 1),
        "Primary n": int(prim_n),
        "Primary % (of n=384)": round(prim_n / total_primary * 100, 1),
    })

# Add "Ash (via VPN)" row — no multi-select column but present in primary
vpn_prim_n = primary_vc.get("Ash (via VPN)", 0)
if vpn_prim_n > 0:
    rows2.append({
        "Source": "Ash (via VPN)",
        "Multi-select n": 0,
        "Multi-select % (of N=393)": 0.0,
        "Primary n": int(vpn_prim_n),
        "Primary % (of n=384)": round(vpn_prim_n / total_primary * 100, 1),
    })

table2 = pd.DataFrame(rows2)
# Remove rows with 0 in both columns
table2 = table2[(table2["Multi-select n"] > 0) | (table2["Primary n"] > 0)]
table2 = table2.sort_values("Multi-select n", ascending=False)
table2.to_csv(os.path.join(OUT_DIR, "table2_sources.csv"), index=False)
print(f"Table 2 saved ({len(table2)} rows)")

# TABLE 3: AI use patterns (among AI users)

gpai_col = find_col(df, "general-purpose ai tools (e.g.")
ai_mask = df[gpai_col] == True
n_ai = ai_mask.sum()

rows3 = []

# Frequency
freq_col = find_col(df, "how often", "general-purpose ai")
freq = df.loc[ai_mask, freq_col].dropna()
freq_vc = freq.value_counts()
for val, cnt in freq_vc.items():
    rows3.append({"Section": "Frequency", "Item": val,
                  "n": cnt, "%": round(cnt / len(freq) * 100, 1)})

# Role
role_col = find_col(df, "fit into your life")
role = df.loc[ai_mask, role_col].dropna()
role_vc = role.value_counts()
for val, cnt in role_vc.items():
    rows3.append({"Section": "Role in life", "Item": val,
                  "n": cnt, "%": round(cnt / len(role) * 100, 1)})

# Use cases (checkbox columns)
usecase_cols = [c for c in df.columns
                if "mainly use general-purpose ai for" in c.lower() and "(" in c]
for col in usecase_cols:
    label = col.split("(")[-1].rstrip(")")
    n = df.loc[ai_mask, col].sum() if df[col].dtype == bool else (df.loc[ai_mask, col] == True).sum()
    rows3.append({"Section": "Use cases", "Item": label,
                  "n": int(n), "%": round(n / n_ai * 100, 1)})

# Motivations (checkbox columns)
motiv_cols = [c for c in df.columns
              if "why did you choose" in c.lower() and "(" in c]
for col in motiv_cols:
    label = col.split("(")[-1].rstrip(")").strip()
    n = df.loc[ai_mask, col].sum() if df[col].dtype == bool else (df.loc[ai_mask, col] == True).sum()
    rows3.append({"Section": "Motivations", "Item": label,
                  "n": int(n), "%": round(n / n_ai * 100, 1)})

table3 = pd.DataFrame(rows3)
table3.to_csv(os.path.join(OUT_DIR, "table3_ai_use.csv"), index=False)
print(f"Table 3 saved ({len(table3)} rows)")

print(f"\nAll tables saved to {OUT_DIR}")
