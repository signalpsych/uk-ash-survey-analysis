"""
03_figures.py
=============
Generates publication-quality figures for the paper:
  - Figure 1: Primary source of support (horizontal bar chart)
  - Figure 2: Motivations for choosing GPAI (horizontal bar chart)
  - Figure 3: Access change + wellbeing (three-panel: all respondents, no-support subgroup, wellbeing)
  - Figure 4: Qualitative themes (horizontal bar chart)

Usage:
    python 03_figures.py

Input:  ../data/UK survey_Submissions_2026-03-16.csv
        ../results/qualitative_summary.txt (for Figure 4)
Output: ../results/fig1_primary_source.png
        ../results/fig2_why_ai.png
        ../results/fig3_access_change.png
        ../results/fig4_qualitative_themes.png
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(SCRIPT_DIR, "..", "data",
                          "UK survey_Submissions_2026-03-16.csv")
OUT_DIR    = os.path.join(SCRIPT_DIR, "..", "results")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Helper ───────────────────────────────────────────────────────────────────
def find_col(df, *keywords):
    for c in df.columns:
        cl = c.lower()
        if all(k.lower() in cl for k in keywords):
            return c
    raise KeyError(f"No column found matching keywords: {keywords}")

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Brand palette: purple + grey
PURPLE      = "#7C3AED"
PURPLE_DARK = "#5B21B6"
PURPLE_MID  = "#8B5CF6"
PURPLE_LIGHT= "#C4B5FD"
RED         = "#DC2626"
GRAY        = "#9CA3AF"
GRAY_LIGHT  = "#D1D5DB"
DARK        = "#374151"

# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
N = len(df)

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Primary source of support
# ══════════════════════════════════════════════════════════════════════════════

primary_col = find_col(df, "which one", "relied")
primary = df[primary_col].dropna()

def classify_primary(val):
    v = str(val).lower().replace("\u2019", "'")
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
    if "vpn" in v or ("still us" in v and "ash" in v):
        return "Ash (via VPN)"
    return "Other"

primary_mapped = primary.map(classify_primary)
pvc = primary_mapped.value_counts()
total_primary = len(primary)

# Exclude zero-count categories
categories = [
    "General-purpose AI",
    "Haven't sought support",
    "Friends, family, or partner",
    "Private therapist / counsellor",
    "Other wellbeing apps",
    "NHS services",
    "Books, podcasts, or self-help",
    "Support groups",
    "Online forums / social media",
    "Other",
]
counts = [pvc.get(c, 0) for c in categories]
pcts = [c / total_primary * 100 for c in counts]

# Purple for GPAI, grey-purple for "haven't sought", grey for rest
colors = [PURPLE, GRAY] + [GRAY_LIGHT] * (len(categories) - 2)

fig, ax = plt.subplots(figsize=(10, 5.5))
y_pos = range(len(categories) - 1, -1, -1)
bars = ax.barh(y_pos, pcts, color=colors, height=0.6, edgecolor="white", linewidth=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=10)
ax.set_xlabel("Percentage of respondents (%)", fontsize=11)
ax.set_title("Figure 1. Primary source of support since Ash became unavailable",
             fontsize=12, fontweight="bold", loc="left")

# Percentage labels
for i, (p, c) in enumerate(zip(pcts, counts)):
    yi = len(categories) - 1 - i
    ax.text(p + 0.8, yi, f"{p:.0f}% (n={c})", va="center", fontsize=9, color=DARK)

# Bracket annotation — pushed further right to avoid overlapping n=104
gpai_y = len(categories) - 1
nosup_y = len(categories) - 2
bracket_x = max(pcts[0], pcts[1]) + 12
ax.annotate("", xy=(bracket_x, gpai_y + 0.15), xytext=(bracket_x, nosup_y - 0.15),
            arrowprops=dict(arrowstyle="-", color=DARK, lw=1.5))
ax.plot([bracket_x - 0.3, bracket_x], [gpai_y + 0.15] * 2, color=DARK, lw=1.5)
ax.plot([bracket_x - 0.3, bracket_x], [nosup_y - 0.15] * 2, color=DARK, lw=1.5)
combined_pct = pcts[0] + pcts[1]
ax.text(bracket_x + 0.8, (gpai_y + nosup_y) / 2,
        f"{combined_pct:.0f}% turned to\ngeneral-purpose AI\nor no support",
        fontsize=9, fontweight="bold", va="center", color=DARK)

ax.set_xlim(0, max(pcts) + 24)
ax.text(0.99, 0.01, f"n = {total_primary}", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=9, color="gray")

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "fig1_primary_source.png"), dpi=300, bbox_inches="tight")
plt.close()
print("\u2713 Figure 1 saved")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Motivations for choosing GPAI
# ══════════════════════════════════════════════════════════════════════════════

gpai_col = find_col(df, "general-purpose ai tools (e.g.")
ai_mask = df[gpai_col] == True
n_ai = ai_mask.sum()

motiv_labels = [
    ("Instant access",                   "instant access"),
    ("Free or low cost",                 "free or low cost"),
    ("Easier than NHS or human support", "easier than nhs"),
    ("More private",                     "more private"),
    ("Felt more helpful than alternatives", "felt more helpful"),
    ("Didn\u2019t want something \u201Cmedical\u201D", "didn\u2019t want something"),
    ("Didn\u2019t know other options",   "didn\u2019t know other"),
]

motiv_data = []
for label, kw in motiv_labels:
    kw_norm = kw.lower().replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    col = [c for c in df.columns
           if kw_norm in c.lower().replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
           and "why did you choose" in c.lower()][0]
    n = df.loc[ai_mask, col].sum()
    motiv_data.append((label, n, n / n_ai * 100))

motiv_data.sort(key=lambda x: x[2])

fig, ax = plt.subplots(figsize=(10, 5))
y_pos = range(len(motiv_data))
pcts_m = [m[2] for m in motiv_data]
ns = [m[1] for m in motiv_data]
labels_m = [m[0] for m in motiv_data]

ax.barh(y_pos, pcts_m, color=PURPLE, height=0.55, edgecolor="white")
ax.set_yticks(y_pos)
ax.set_yticklabels(labels_m, fontsize=10)
ax.set_xlabel("Percentage of AI users (%)", fontsize=11)
ax.set_title("Figure 2. Motivations for choosing general-purpose AI for emotional support",
             fontsize=12, fontweight="bold", loc="left")

for i, (p, n) in enumerate(zip(pcts_m, ns)):
    ax.text(p + 0.8, i, f"{p:.0f}% (n={n})", va="center", fontsize=9, color=DARK)

ax.set_xlim(0, max(pcts_m) + 12)
ax.text(0.99, 0.01, f"Among respondents who selected GPAI as a support source (n = {n_ai})",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color="gray")

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "fig2_why_ai.png"), dpi=300, bbox_inches="tight")
plt.close()
print("\u2713 Figure 2 saved")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3: Access change (all respondents vs no-support subgroup) + wellbeing
# ══════════════════════════════════════════════════════════════════════════════

access_col = find_col(df, "access to support changed")
access_order = ["Much better", "A bit better", "About the same", "A bit worse", "Much worse"]

access_all = df[access_col].dropna()
all_vc = access_all.value_counts()
all_pcts = [all_vc.get(k, 0) / len(access_all) * 100 for k in access_order]

nosup_mask = primary_mapped == "Haven't sought support"
nosup_idx = primary[nosup_mask].index
access_nosup = df.loc[nosup_idx, access_col].dropna()
nosup_vc = access_nosup.value_counts()
nosup_pcts = [nosup_vc.get(k, 0) / len(access_nosup) * 100 for k in access_order]

# Wellbeing data
wellbeing_col = find_col(df, "general wellbeing")
wellbeing_order = [
    "Much better than usual",
    "Slightly better than usual",
    "The same as usual",
    "Slightly worse than usual",
    "Much worse than usual",
]
wellbeing_all = df[wellbeing_col].dropna()
wb_vc = wellbeing_all.value_counts()
wb_pcts = [wb_vc.get(k, 0) / len(wellbeing_all) * 100 for k in wellbeing_order]

# Wellbeing for no-support subgroup
wb_nosup = df.loc[nosup_idx, wellbeing_col].dropna()
wb_nosup_vc = wb_nosup.value_counts()
wb_nosup_pcts = [wb_nosup_vc.get(k, 0) / len(wb_nosup) * 100 for k in wellbeing_order]

# Purple gradient: lighter (better) -> gray (same) -> deeper purple (worse)
bar_colors = ["#C4B5FD", "#DDD6FE", GRAY, "#8B5CF6", PURPLE_DARK]

# 2x2 layout: Row 1 = access change, Row 2 = wellbeing
fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharey=True)
(ax1, ax2), (ax3, ax4) = axes

all_worse = all_pcts[3] + all_pcts[4]
nosup_worse = nosup_pcts[3] + nosup_pcts[4]
wb_worse = wb_pcts[3] + wb_pcts[4]
wb_nosup_worse = wb_nosup_pcts[3] + wb_nosup_pcts[4]

wb_short_labels = ["Much better", "Slightly better", "The same", "Slightly worse", "Much worse"]

# Row 1: Access change
for ax, pcts_data, title, n_label, worse_pct, ylabels in [
    (ax1, all_pcts, "A. Access to support \u2014 All respondents", f"n = {len(access_all)}", all_worse, access_order),
    (ax2, nosup_pcts, "B. Access to support \u2014 No-support subgroup", f"n = {len(access_nosup)}", nosup_worse, access_order),
]:
    y_pos = range(len(ylabels) - 1, -1, -1)
    ax.barh(y_pos, pcts_data, color=bar_colors, height=0.6, edgecolor="white")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ylabels, fontsize=10)
    ax.set_xlabel("%", fontsize=11)
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    for i, p in enumerate(pcts_data):
        yi = len(ylabels) - 1 - i
        ax.text(p + 1, yi, f"{p:.0f}%", va="center", fontsize=9, color=DARK)
    ax.set_xlim(0, max(pcts_data) + 12)
    ax.text(0.98, 0.02, n_label, transform=ax.transAxes, ha="right", fontsize=9, color="gray")
    ax.text(0.98, 0.97, f"Total worse: {worse_pct:.0f}%", transform=ax.transAxes,
            ha="right", va="top", fontsize=10, fontweight="bold", color=PURPLE_DARK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#EDE9FE", edgecolor=PURPLE_LIGHT, alpha=0.9))

# Row 2: Wellbeing
for ax, pcts_data, title, n_label, worse_pct in [
    (ax3, wb_pcts, "C. General wellbeing \u2014 All respondents", f"n = {len(wellbeing_all)}", wb_worse),
    (ax4, wb_nosup_pcts, "D. General wellbeing \u2014 No-support subgroup", f"n = {len(wb_nosup)}", wb_nosup_worse),
]:
    y_pos = range(len(wb_short_labels) - 1, -1, -1)
    ax.barh(y_pos, pcts_data, color=bar_colors, height=0.6, edgecolor="white")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(wb_short_labels, fontsize=10)
    ax.set_xlabel("%", fontsize=11)
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    for i, p in enumerate(pcts_data):
        yi = len(wb_short_labels) - 1 - i
        ax.text(p + 1, yi, f"{p:.0f}%", va="center", fontsize=9, color=DARK)
    ax.set_xlim(0, max(pcts_data) + 12)
    ax.text(0.98, 0.02, n_label, transform=ax.transAxes, ha="right", fontsize=9, color="gray")
    ax.text(0.98, 0.97, f"Total worse: {worse_pct:.0f}%", transform=ax.transAxes,
            ha="right", va="top", fontsize=10, fontweight="bold", color=PURPLE_DARK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#EDE9FE", edgecolor=PURPLE_LIGHT, alpha=0.9))

fig.suptitle("Figure 3. Perceived change in access to support and general wellbeing",
             fontsize=13, fontweight="bold", x=0.01, ha="left")
plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(os.path.join(OUT_DIR, "fig3_access_change.png"), dpi=300, bbox_inches="tight")
plt.close()
print("\u2713 Figure 3 saved")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Qualitative themes
# ══════════════════════════════════════════════════════════════════════════════

# Run qualitative coding inline to get theme counts
import re, sys
freetext_col = [c for c in df.columns if "better" in c.lower() and "worse" in c.lower()][0]
responses = df[freetext_col].dropna().reset_index()
responses.columns = ["orig_idx", "text"]
responses = responses[responses["text"].str.strip().str.len() > 5].copy()

# Read the codebook from script 02 results
coded = pd.read_csv(os.path.join(OUT_DIR, "coded_responses.csv"))
total_coded = len(coded)

# Count themes from coded_responses
theme_labels = {
    "T1_GPAI_INFERIOR":           "GPAI inferior to Ash",
    "T2_GPAI_ADEQUATE":           "GPAI adequate substitute",
    "T3_NO_REPLACEMENT_FOUND":    "No replacement found",
    "T4_NHS_ACCESS_BARRIER":      "NHS access barrier",
    "T5_HUMAN_PREFERRED_INACCESSIBLE": "Human support preferred\nbut inaccessible",
    "T6_HUMAN_ACCESSED":          "Accessing human\nprofessional",
    "T7_MEMORY_CONTINUITY":       "Memory / continuity\nvalued",
    "T8_INSIGHTS_REFLECTIONS":    "Insights / reflections\nvalued",
    "T9_AVAILABILITY_24_7":       "24/7 availability valued",
    "T10_PRIVACY_TRUST_SAFETY":   "Privacy / trust / safety\nvalued",
    "T11_DISTRESS_AT_LOSS":       "Distress at losing Ash",
    "T12_VPN_WORKAROUND":         "VPN workaround",
    "T13_ASH_CRITIQUE":           "Critique of Ash",
    "T14_OTHER_WELLBEING_APP":    "Switched to other app",
    "T15_SELF_MANAGE_INFORMAL":   "Self-managing /\ninformal support",
}

# Domain groupings for coloring
domain_colors = {
    "T1_GPAI_INFERIOR": PURPLE,
    "T2_GPAI_ADEQUATE": PURPLE,
    "T3_NO_REPLACEMENT_FOUND": "#6366F1",  # indigo
    "T4_NHS_ACCESS_BARRIER": "#6366F1",
    "T5_HUMAN_PREFERRED_INACCESSIBLE": "#6366F1",
    "T6_HUMAN_ACCESSED": "#6366F1",
    "T7_MEMORY_CONTINUITY": PURPLE_MID,
    "T8_INSIGHTS_REFLECTIONS": PURPLE_MID,
    "T9_AVAILABILITY_24_7": PURPLE_MID,
    "T10_PRIVACY_TRUST_SAFETY": PURPLE_MID,
    "T11_DISTRESS_AT_LOSS": PURPLE_DARK,
    "T12_VPN_WORKAROUND": GRAY,
    "T13_ASH_CRITIQUE": GRAY,
    "T14_OTHER_WELLBEING_APP": GRAY,
    "T15_SELF_MANAGE_INFORMAL": GRAY,
}

theme_counts = {}
for code in theme_labels:
    n = coded["codes_str"].str.contains(code, na=False).sum()
    theme_counts[code] = n

# Sort by count descending
sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1])

fig, ax = plt.subplots(figsize=(10, 7))
y_pos = range(len(sorted_themes))
bars_data = [t[1] for t in sorted_themes]
bars_pcts = [t[1] / total_coded * 100 for t in sorted_themes]
bars_labels = [theme_labels[t[0]] for t in sorted_themes]
bars_colors = [domain_colors[t[0]] for t in sorted_themes]

ax.barh(y_pos, bars_pcts, color=bars_colors, height=0.6, edgecolor="white")
ax.set_yticks(y_pos)
ax.set_yticklabels(bars_labels, fontsize=9)
ax.set_xlabel("Percentage of analyzable responses (%)", fontsize=11)
ax.set_title("Figure 4. Qualitative themes in free-text responses",
             fontsize=12, fontweight="bold", loc="left")

for i, (p, n) in enumerate(zip(bars_pcts, bars_data)):
    ax.text(p + 0.5, i, f"{p:.0f}% (n={n})", va="center", fontsize=8.5, color=DARK)

ax.set_xlim(0, max(bars_pcts) + 10)

# Legend for domain colors
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=PURPLE, label="Evaluation of GPAI"),
    Patch(facecolor="#6366F1", label="Support gap"),
    Patch(facecolor=PURPLE_MID, label="Valued features of a purpose-built tool"),
    Patch(facecolor=PURPLE_DARK, label="Emotional response to loss"),
    Patch(facecolor=GRAY, label="Coping strategies"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=8.5,
          framealpha=0.9, edgecolor=GRAY_LIGHT)

ax.text(0.99, 0.01, f"n = {total_coded} analyzable responses",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color="gray")

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "fig4_qualitative_themes.png"), dpi=300, bbox_inches="tight")
plt.close()
print("\u2713 Figure 4 saved")

print(f"\nAll figures saved to {OUT_DIR}")
