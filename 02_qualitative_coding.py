"""Coding of free-text survey responses (Q9).

Applies the study codebook (15 codes, regex patterns per code) to all
analyzable responses, with manually reviewed reclassifications where
patterns missed clearly codable content. Writes results/coded_responses.csv
and results/qualitative_summary.txt.
"""

import os, re, sys
import pandas as pd
import numpy as np

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(SCRIPT_DIR, "..", "data",
                          "UK survey_Submissions_2026-03-16.csv")
OUT_DIR    = os.path.join(SCRIPT_DIR, "..", "results")
os.makedirs(OUT_DIR, exist_ok=True)
CODED_PATH = os.path.join(OUT_DIR, "coded_responses.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "qualitative_summary.txt")

# Load data
df = pd.read_csv(DATA_PATH)
# Find free-text column (Q9)
freetext_col = [c for c in df.columns if "better" in c.lower() and "worse" in c.lower()][0]
responses = df[freetext_col].dropna().reset_index()
responses.columns = ["orig_idx", "text"]
# Filter out empty / trivially short responses
responses = responses[responses["text"].str.strip().str.len() > 5].copy()

print(f"Free-text responses to code: {len(responses)}")

# CODEBOOK: 15 codes across 6 thematic domains
# Each code has a list of regex patterns. A response is assigned a code if
# ANY pattern matches (case-insensitive). Patterns were developed inductively
# from reading responses and refined over three coding passes.

CODEBOOK = {
    # Domain 1: GPAI Experience
    "T1_GPAI_INFERIOR": [
        r"chatgpt.{0,30}(not|isn.t|wasn.t|doesn.t|lacks?|miss|worse|poor|generic|impersonal|cold|limit|shallow|superfic)",
        r"(gpt|gemini|claude|copilot|ai).{0,30}(not|isn.t|doesn.t|lacks?|miss|worse|poor|generic|impersonal|cold|limit|shallow|superfic|pale|rubbish|terrible|awful|hopeless|useless|nowhere near|can.t compare|not the same|no substitute|nothing like|inferior|inadequate|no comparison|disappointing|frustrat)",
        r"(not|isn.t|doesn.t|wasn.t|nowhere near).{0,30}(as good|the same|a replacement|comparable|a substitute|like ash|what ash)",
        r"(worse|inferior|pales?|lacking).{0,30}(than ash|compared|to ash|comparison)",
        r"nothing.{0,20}(compares?|comes? close|works? as well|like ash|as good)",
        r"(tried|using|use).{0,30}(chatgpt|gpt|gemini|claude|copilot|ai).{0,30}(but|however|though)",
        r"no\b.{0,10}\b(it|they|nothing|none).{0,20}(worse|don.t|doesn.t|isn.t|not)",
        r"(miss|missed|missing).{0,15}ash",
        r"ash was (better|superior|more|unique|special)",
        r"(gpt|chatgpt|ai).{0,20}(feel|felt).{0,15}(cold|impersonal|generic|robotic|empty|hollow|flat|off|weird|strange|wrong|clinical|sterile)",
        # Broader: alternatives described as worse/generic/lacking without naming specific tool
        r"\b(worse|generic|lacking|less interactive|less personal)\b(?!.{0,15}(ash|than usual))",
        r"(alternatives?|other.{0,5}(app|tool|ai|service)).{0,15}(worse|generic|lacking|not as|aren.t as|pale|inferior)",
        r"(none|no).{0,5}(of the|the).{0,10}(alternative|speaking|other).{0,10}(as good|good)",
        r"ash (did|does|was).{0,10}(much |far |way )?(better|more)",
        r"(isn.t|not).{0,10}(as (evidenced|nuanced|dynamic|specific|enhanced|targeted|relevant|interactive|personal))",
    ],

    "T2_GPAI_ADEQUATE": [
        r"chatgpt.{0,30}(help|good|okay|ok\b|fine|decent|works?|useful|great|similar|adequate|sufficient|close|alright|not bad|pretty good)",
        r"(gpt|gemini|claude|copilot).{0,20}(help|good|okay|ok\b|fine|decent|works?|useful|great|similar|adequate|sufficient|close|alright|not bad|pretty good|does the job|gets the job|does a job|manage|satisf|reasonable|comparable|works? well)",
        r"(ai|chatgpt|gpt).{0,20}(has been|is).{0,10}(help|good|useful|great|ok|fine|decent|valuable|beneficial)",
        r"(gpt|ai|chatgpt).{0,20}(fill|bridge).{0,10}(gap|void|hole)",
        # Explicit "same as" / "similar" / "no different" comparisons
        r"(the same|same really|does the same|similar|no.{0,3}different)",
        r"(claude|chatgpt|gpt|gemini).{0,15}(is |are )?(much |quite |pretty )?(good|better|great|excellent|leads to better)",
        r"(i like|i prefer).{0,10}(chatgpt|claude|gemini|gpt)",
    
        # Broader adequacy patterns
        r"(not sure|not very).{0,10}(different|distinct)",
        r"(gemini|claude|gpt).{0,10}(has |have )?(a )?(wider|broader|more|better)",
        # Removed: "created an agent AI" pattern — too broad, catches non-evaluative mentions
    ],

    # Domain 2: Support Gap
    "T3_NO_REPLACEMENT_FOUND": [
        r"no(thing|t| |\b).{0,20}(work|help|replac|compar|substitute|alternative|option|match|equivalent)",
        r"(haven.t|have not|not).{0,15}found.{0,15}(any|replace|alternative|substitute|support)",
        r"^nothing\b.{0,30}$",  # short "Nothing" / "Nothing really" / "Nothing yet" responses
        r"nothing.{0,15}(compares?|comes? close|works?|like|as good|else|out there|available|helped|close|better|match|similar)",
        r"nothing (has come|is as|i can|that|i.ve found|else|out there|available)",
        r"(can.t|cannot|couldn.t) find",
        r"(no|without).{0,15}(support|help|replacement|alternative)",
        r"(left|leaving|leaves?).{0,15}(without|gap|void|hole|nothing)",
        r"(gap|void|hole|vacuum).{0,15}(left|since|without|in)",
        r"(still|just).{0,15}(looking|searching|waiting|hoping)",
        r"(haven.t|have not|not).{0,15}(us|using|tried|found|got).{0,15}(any|something|a replacement|an alternative|anything)",
        r"there (is |are )?(no|nothing|not).{0,15}(good|suitable|adequate|comparable|equivalent|similar|like|replacement|alternative|substitute|option|tool|app)",
        r"(haven.t|have not|not).{0,15}(been able to|managed to).{0,15}(find|get|access|replace)",
        r"(not using|not found|haven.t got).{0,10}(any|a |an )",
        # Short negative responses to "anything better or worse?" = no replacement found
        r"^(no|nope|nah|nahhhh|not really|not necessarily|no i don.t think so|no not really|not that i can think of|not at the moment|no better|i (don.t|wouldn.t) (think|say))\b.{0,20}$",
        # "isn't anything like it" / "yet to find"
        r"(isn.t|not).{0,10}(anything|something).{0,10}(like it|like ash|similar|else)",
        r"(haven.t|have not).{0,10}(sought|looked|searched|tried)",
        r"(yet to find|haven.t found|can.t find)",
    
        # Positive evaluation of Ash (implies no replacement found)
        r"^.{0,5}ash (was|is) (the best|amazing|great|good|wonderful|fantastic|brilliant|incredible|very good|really good|excellent|perfect|super)\b",
        r"^no.{0,5}(ash|i|it).{0,10}(was|is|think).{0,10}(the best|amazing|great|good|wonderful|very good|really good|excellent)",
        r"(cannot|can.t) praise.{0,10}(ash|it|enough)",
        r"^.{0,10}(one of the best|the best).{0,10}(support|app|tool|ai)",
        # Additional patterns for uncoded responses
        r"(haven.t|have not|not).{0,10}(got|getting|received).{0,10}(the |any )?(help|support)",
        r"bottling.{0,10}(up|things|it)|no one to talk to",
        r"wasn.t able to use.{0,10}(ash|it|the app)",
        r"(trying to|i.m).{0,10}(lessen|reduce|cut down|stop)",
        r"(more busy|too busy|busy than usual)",
        r"(love|like|want).{0,5}(to have |)(ash|it).{0,5}back",
        r"(helpful|good|great|useful|calming).{0,10}(additional|extra|support|source|tool)",
    ],

    "T4_NHS_ACCESS_BARRIER": [
        r"nhs.{0,30}(wait|long|slow|months|years|underfunded|overwhelmed|inaccessible|impossible|difficult|hard|struggle|queue|list|cant|can.t|unable|backlog|overcapacity|fail|inadequate|useless|terrible|awful|joke|laughable|not available|unavailable|shortage)",
        r"(gp|doctor|therapist).{0,20}(wait|long|slow|months|years|queue|list|cant|can.t|unable|unavailable|won.t|refused|wouldn.t|no appointment|fully booked|booked up)",
        r"(waiting|waited|wait).{0,15}(list|time|months|years|ages|forever|long|too long)",
        r"(mental health).{0,20}(services?|support).{0,15}(wait|long|unavailable|inaccessible|inadequate|overwhelmed|overloaded)",
    ],

    "T5_HUMAN_PREFERRED_INACCESSIBLE": [
        r"(prefer|want|need|wish|like|love).{0,20}(therapist|counsell|human|person|someone|real|professional|face.to.face|in.person)",
        r"(therapist|counsell|professional|human).{0,20}(but|however|though|yet|unfortunately|can.t|cannot|afford|expensive|too|cost|wait|unavailable|no access|hard to)",
        r"(can.t|cannot|couldn.t|unable to).{0,15}(afford|access|get|find|see).{0,15}(therapist|counsell|professional|help|support)",
        r"(too expensive|can.t afford|cost|unaffordable|pricey|priced out)",
    ],

    "T6_HUMAN_ACCESSED": [
        r"(seeing|see|started|got|have|attend|going|go to|found|been to|referred|with|switched to).{0,15}(a |my )?(therapist|counsell|psycholog|psychiatr|professional|gp|doctor|cbt|talk therapy|talking therap)",
        r"(therapist|counsell|psycholog|cbt|professional|therapy).{0,20}(help|good|great|useful|works?|better|effective|beneficial|support|is working|has been)",
        r"(therapy|counselling|cbt|sessions?).{0,10}(weekly|fortnightly|monthly|regular|ongoing|started|beginning|began|now|currently)",
        r"(private|nhs).{0,10}(therapy|therapist|counsell|support|psycholog)",
        # Standalone mentions of accessing a professional
        r"^(counsell|therapist|video therapy|talking to.{0,10}(certified |)(therapist|counsell))",
        r"(human|actual).{0,10}(listening|support|therapist|counsell|help)",
    
        r"(human|real).{0,10}(being|person|relationship|support).{0,10}(irl|in real life|is |are )?(prefer|better|good)",
    ],

    # Domain 3: What Ash Provided
    "T7_MEMORY_CONTINUITY": [
        r"(ash|chatgpt|gpt|gemini|claude|copilot|ai|app|tool).{0,30}(remember|recall|knew|know me|context|history|continuity|follow.up|personaliz|personalis|tailor|adapted|learned about)",
        r"(remember|memory|context|continuity|personaliz|personalis|persistent|tailored).{0,20}(ash|chatgpt|gpt|gemini|claude|copilot|ai|app|session|conversation)",
        r"(lack|miss|without|no|doesn.t have|don.t have|didn.t have|hasn.t got|lost).{0,15}(memory|continuity|context|history|personali[sz])",
        r"(didn.t|doesn.t|don.t|can.t|couldn.t|won.t|wouldn.t).{0,15}(remember|recall|know).{0,15}(me|my|what|who|previous|last|before)",
        r"(conversation|chat).{0,15}(history|continuity|context|previous|thread|memory)",
        r"(more|less|not).{0,10}(personal|personalised|personalized)\b(?!.{0,5}(counsell|therapist|coach))",
        r"(previous|past|earlier|prior|last).{0,10}(conversation|session|chat|discussion)",
        r"(follow.up|follow up|followed up|following up).{0,10}(on|about|with|question|prompt)",
        r"(back ?story|back.ground|knew what|know what|knew about|historic)",
        r"(build|built).{0,10}(relationship|rapport|understanding).{0,10}(with|over)",
        r"(tailored|customised|customized|bespoke).{0,10}(to|for|approach|support|advice|need)",
    
        r"(separate|dedicated|own|specific).{0,10}(app|tool|space)",
    ],

    "T8_INSIGHTS_REFLECTIONS": [
        r"(insight|reflect(?:ion|ed|ing)|self.aware|perspectiv|pattern|breakthrough|revelation|epiphan|realisation|realization|eye.open|clarity)",
        r"(ash|it|the app).{0,20}(help|helped|helped me).{0,15}(understand|see|reali[sz]|reflect|process|think|work through|figure out|grow|perspective|aware)",
        r"(weekly |daily )?(reflect|insight|journal).{0,10}(feature|section|prompt|summar)",
    
        r"(calming|measured|soothing|gentle).{0,10}(and |)(calming|measured|soothing|gentle|approach|tone|way)",
    ],

    "T9_AVAILABILITY_24_7": [
        r"(24.?7|always available|always there|any ?time|anytime|middle of.{0,10}night|3.?am|2.?am|late at night|early hours|whenever|round the clock|around the clock|all hours|on demand)",
        r"(available|access|there|respond|support).{0,15}(whenever|always|anytime|24|night|morning|early|late|immediately|instantly|straight away|right away)",
        r"(can.t|couldn.t|aren.t|isn.t|not).{0,10}(be there|available|accessible).{0,10}(24|always|all the time|whenever|when i need|in the moment|on demand)",
        r"(deal|help|support|talk|vent|rationalise|process).{0,15}(in the moment|right then|right away|there and then|when.{0,5}(need|happen|feel|come up))",
        r"always.{0,5}(available|there|on|accessible|open)",
    ],

    "T10_PRIVACY_TRUST_SAFETY": [
        # Trust and safety in context of AI/Ash
        r"(safe|safety|trust|trusted|trustworthy).{0,15}(ash|app|ai|tool|space|environment|built|designed|programmed)",
        r"(ash|it|the app).{0,15}(safe|trusted|non.?judg|didn.t judge|doesn.t judge|no judg|without judg)",
        # Privacy as a valued feature (not "private therapist")
        r"(privacy|confidential|anonymous|discreet).{0,10}(ash|app|ai|tool|of|with|about|valued|important)",
        r"(more |feel |felt )private\b(?!.{0,5}(therapist|counsell|therapy|practice))",
        # Comfort sharing with AI vs humans
        r"(don.t|didn.t|couldn.t|can.t|won.t|wouldn.t).{0,15}(tell|share|talk|open|discuss|say|admit|confide).{0,15}(anyone|someone|people|friends|family|partner|therapist|gp|doctor|human)",
        r"(easier|comfortable|more comfortable).{0,15}(talk|share|open|discuss|say|admit|confide).{0,15}(to |with )?(ai|ash|chatgpt|bot|machine|it|app)",
        # Non-judgmental explicitly
        r"(non.?judg|no.?judg|without judg|didn.t judge|doesn.t judge|not judge|won.t judge)",
        # Fear of stigma / embarrassment in help-seeking
        r"(embarrass|stigma|afraid|scared).{0,15}(tell|share|talk|ask|seek|admit|open up)",
        # Worry about what AI does with data
        r"(worry|concerned|anxious).{0,10}(what|about|data|privacy|sharing|tell)",
        # Don't feel safe with GPAI specifically
        r"(don.t|didn.t|doesn.t).{0,10}(feel |)(safe|trust).{0,10}(other|general|gpt|chatgpt|ai|them)",
    
        # Less judgmental than human
        r"(less|not|no|without).{0,5}(judg|judge ?mental)",
    ],

    # Domain 4: Distress / Loss
    "T11_DISTRESS_AT_LOSS": [
        # Explicit distress language
        r"(devastat|gutted|heartbr|grief|griev|mourn|bereft|desperate|despairing|helpless|hopeless|crushed|shattered|struggling without|suffering)",
        # Missing Ash specifically
        r"(miss|missed|missing).{0,15}(ash|it|the app|slingshot|having|being able|access|support|using)",
        # Wanting Ash back (active longing)
        r"(bring|need|wish|please|hope|pray|beg).{0,15}(back|return|restore|ash|it|slingshot|app|available)",
        r"(please|pls).{0,10}(bring|come|return|make).{0,10}(back|available|it)",
        # Don't know what to do without it
        r"(don.t|didn.t|wouldn.t) know what.{0,10}(do|would|i.d)",
        # Explicit emotional impact of losing Ash
        r"(really|so|very|extremely|deeply|incredibly|genuinely|truly).{0,10}(miss|sad|upset|devastat|disappoint|frustrat|struggled|struggling|affected|lost)",
        r"(i|we) (loved|love) ash",
        r"(without ash|since ash|losing ash|ash going|ash being removed).{0,15}(i|my|it|life|things|everything).{0,15}(worse|harder|difficult|struggle|suffer|deteriorat|decline|down|bad)",
        # Ash as lifeline (implies distress at loss, not just praise)
        r"(ash|it).{0,10}(was|is|meant|been).{0,5}(everything|lifeline|lifesaver|a lifeline|my lifeline|crucial|vital|essential)",
        r"(relied|depend|lean|count).{0,10}(on)?.{0,5}(ash|it|the app|slingshot)",
        # Explicit loss/grief framing
        r"(losing|lost|loss of).{0,10}(ash|access|it|the app|slingshot)",
        r"(gutted|devastated|upset|frustrated|angry|disappointed).{0,10}(it|ash|that|about|when|since)",
        # Want/love/like it back, shame it's gone
        r"(want|like|love|need).{0,5}(ash|it).{0,5}back",
        r"(shame|disappointing|disappointed).{0,10}(ash|it|that|gone|removed|unavailable|taken away|closed|not available)",
    ],

    # Domain 5: Workarounds
    "T12_VPN_WORKAROUND": [
        r"vpn",
        r"(still|continu).{0,10}(use|using|access).{0,10}(ash|slingshot|it|the app)",
        r"(found|use|using|got|get|set up).{0,10}(a |)(way|method|workaround|work.around|trick|hack|bypass|route)",
    ],

    "T14_OTHER_WELLBEING_APP": [
        r"(headspace|calm\b|woebot|wysa|youper|talkspace|betterhelp|7 cups|seven cups|sanvello|moodfit|daylio|happify|bloom|flow|unmind|silvercloud|ieso|kooth|shout|hub of hope|togetherall|cove|mind ?doc|aura|insight timer|meditopia|mindshift|feelmo|intellect|replika|pi\.ai|character\.ai|hume|noah\b|onsen|nova\b|abby\b|brenda\b|frank\b|dbt coach|goalpost|myanima|ifs guide)",
        r"(other|another|different|new|alternative).{0,15}(app|apps|platform|tool|service|programme|program)",
        r"(using|use|tried|try|download|found|switch|moved to|started|started using).{0,15}(an? |)(app|platform|tool|programme|program)",
    
        r"(static|other|different).{0,10}(resource|resources)",
    ],

    "T15_SELF_MANAGE_INFORMAL": [
        r"(journal|diary|write|writing|notes|meditation|meditat|mindful|yoga|exercise|gym|walk|walking|running|run |cycling|swim|reading|read |books?|podcast|music|art|creative|paint|draw|garden|nature|outdoors|prayer|pray|faith|church|religion|spiritual|breathing|breath work|breathwork)",
        r"(cope|coping|manage|managing|deal|dealing|get by|getting by|survive|surviving|carry on|soldier|muddle|push through|press on|on my own|by myself|myself|self.care|self care|selfcare)",
        r"(talk|talking|speak|lean|leaning|turn|turned|turning).{0,10}(to |on )?(friends?|family|partner|wife|husband|mum|dad|mother|father|sister|brother)",
        r"(friends?|family|partner).{0,10}(help|support|talk|listen|there for|been there|step|stepped)",
        r"(medication|medic|meds)\b",
        r"(own|my).{0,5}(advice|strateg|coping|techniques)",
        # Bare GPAI name = "this is what I'm using now" (coping, not evaluation)
        r"^(chatgpt|chat gpt|claude|gemini|copilot|grok)\s*$",
    
        # Other informal coping
        r"\b(boyfriend|girlfriend)\b",
        r"^ai support\s*$",
        r"\bthc\b",
    ],

    # Domain 6: Ash Critique
    "T13_ASH_CRITIQUE": [
        r"ash.{0,30}(repetit|generic|scripted|robotic|rigid|inflexible|basic|superfic|patroni[sz]|condescend|tedious|clunky|stilted|annoying|frustrat|slow|bug|glitch|crash)",
        r"(ash|slingshot).{0,20}(problem|issue|downside|weakness|limitation|flaw|complaint|frustrat|disappoint|annoy)",
        r"(didn.t|don.t|wasn.t|isn.t).{0,10}(like|enjoy|appreciate|rate).{0,10}(ash|slingshot|the app)",
        r"ash.{0,15}(couldn.t|wouldn.t|didn.t|wasn.t able to).{0,15}(help|stop|handle|understand|provide|do|offer|manage)",
        r"ash.{0,10}(kept|would|used to|always|sometimes|often).{0,15}(repeat|ask|say|do|give|respond|loop|circle|same|over and over|non.?stop|nonstop)",
        r"ash.{0,10}(speak|spoke|talk|respond|sound).{0,15}(like a robot|robotic|too much|mechanical|stiff)",
        r"ash (didn.t|didn.t really|never|wasn.t).{0,5}work",
        r"ash.{0,10}(needs? to|should|could).{0,15}(improv|use|be more|change|add|do|have|incorporat|develop)",
        r"(only|one|main).{0,10}(complaint|criticism|issue|problem|thing|gripe|concern|drawback|downside|negative).{0,20}(ash|with ash|about ash|is|was)",
        r"ash.{0,10}(talk|spoke|went).{0,10}(in circles|round in circles|nowhere)",
        r"(found|find).{0,5}(ash|it).{0,10}(lacking|really lacking|limited|basic)",
    
        r"(doesn.t|don.t|not).{0,10}(support).{0,10}(other |my |the )?(language)",
    ],
}

# CODING ENGINE

def code_response(text):
    """Apply all codes to a single response. Returns list of matching code names."""
    matched = []
    for code, patterns in CODEBOOK.items():
        for pat in patterns:
            try:
                if re.search(pat, text, re.IGNORECASE):
                    matched.append(code)
                    break
            except re.error:
                continue
    return matched

# Apply coding
responses["codes"] = responses["text"].apply(code_response)
responses["codes_str"] = responses["codes"].apply(
    lambda x: ", ".join(x) if x else "UNCODED"
)
responses["n_codes"] = responses["codes"].apply(len)

# MANUAL OVERRIDES (lead author review)
# Reviewed by CAS; assigned where patterns missed clearly codable content.
# Keys are row indices in the raw survey dataframe.

MANUAL_OVERRIDES = {
    9:   ["T3_NO_REPLACEMENT_FOUND"],            # unmet need for help
    18:  ["T3_NO_REPLACEMENT_FOUND"],            # keeping feelings inside; no one to talk to
    21:  ["T10_PRIVACY_TRUST_SAFETY"],           # AI felt less judgmental than a person
    43:  ["T2_GPAI_ADEQUATE"],                   # saw little difference from a general-purpose AI session
    63:  ["T2_GPAI_ADEQUATE"],                   # preferred another assistant's responses
    70:  ["T6_HUMAN_ACCESSED"],                  # prefers in-person support; not accessible
    85:  ["T15_SELF_MANAGE_INFORMAL"],           # bare mention of AI support
    95:  ["T15_SELF_MANAGE_INFORMAL"],           # substance-based coping
    103: ["T8_INSIGHTS_REFLECTIONS"],            # found Ash calming and measured
    127: ["T3_NO_REPLACEMENT_FOUND"],            # valued Ash as an additional, hard-to-find support
    146: ["T3_NO_REPLACEMENT_FOUND"],            # wants Ash back
    150: ["T13_ASH_CRITIQUE"],                   # missing language support
    172: ["T2_GPAI_ADEQUATE"],                   # another assistant knows them better
    195: ["T14_OTHER_WELLBEING_APP"],            # shifted to static self-help resources
    243: ["T7_MEMORY_CONTINUITY"],               # valued having a dedicated app
    268: ["T15_SELF_MANAGE_INFORMAL"],           # built a custom assistant (use, not evaluation)
    295: ["T3_NO_REPLACEMENT_FOUND"],            # cutting down phone use
    315: ["T3_NO_REPLACEMENT_FOUND"],            # brief praise, no alternative named
    350: ["T7_MEMORY_CONTINUITY", "T8_INSIGHTS_REFLECTIONS"],  # valued follow-up prompts
    351: ["T3_NO_REPLACEMENT_FOUND"],            # no alternative; busier than usual
    367: ["T15_SELF_MANAGE_INFORMAL"],           # new relationship as support
    369: ["T3_NO_REPLACEMENT_FOUND"],            # little chance to use Ash before withdrawal
    381: ["T15_SELF_MANAGE_INFORMAL"],           # uses general AI and talks to people (coping)
    385: ["T1_GPAI_INFERIOR"],                   # called Ash an enhanced version of general tools
}

for orig_idx, override_codes in MANUAL_OVERRIDES.items():
    mask = responses["orig_idx"] == orig_idx
    if mask.any():
        idx = responses.index[mask][0]
        existing = responses.at[idx, "codes"]
        if not existing:  # was UNCODED
            responses.at[idx, "codes"] = override_codes
        else:
            responses.at[idx, "codes"] = list(set(existing + override_codes))

# Recompute codes_str and n_codes after overrides
responses["codes_str"] = responses["codes"].apply(
    lambda x: ", ".join(sorted(x)) if x else "UNCODED"
)
responses["n_codes"] = responses["codes"].apply(len)

# SUMMARY STATISTICS
output_lines = []
def printb(*args, **kwargs):
    import io
    buf = io.StringIO()
    print(*args, file=buf, **kwargs)
    text = buf.getvalue()
    sys.stdout.write(text)
    output_lines.append(text)

total = len(responses)
coded = (responses["n_codes"] > 0).sum()
uncoded = total - coded

printb("=" * 70)
printb("QUALITATIVE CODING SUMMARY")
printb("=" * 70)
printb(f"Total free-text responses: {total}")
printb(f"Coded (≥1 theme):    {coded} ({coded/total*100:.1f}%)")
printb(f"Uncoded:             {uncoded} ({uncoded/total*100:.1f}%)")
printb(f"Mean codes/response: {responses['n_codes'].mean():.2f}")
printb(f"Max codes/response:  {responses['n_codes'].max()}")

printb(f"\n{'Code':<35} {'n':>5} {'% of coded':>10} {'% of total':>10}")
printb("-" * 65)

# Count each code
code_counts = {}
for code in CODEBOOK:
    n = responses["codes"].apply(lambda x: code in x).sum()
    code_counts[code] = n

# Sort by frequency
for code, n in sorted(code_counts.items(), key=lambda x: -x[1]):
    printb(f"  {code:<33} {n:>5} {n/coded*100:>9.1f}% {n/total*100:>9.1f}%")

# Domain-level summary
printb("\n\nTHEMATIC DOMAINS:")
printb("-" * 65)
domains = {
    "Evaluation of AI tools": ["T1_GPAI_INFERIOR", "T2_GPAI_ADEQUATE", "T13_ASH_CRITIQUE"],
    "Support Gap":            ["T3_NO_REPLACEMENT_FOUND", "T4_NHS_ACCESS_BARRIER",
                               "T5_HUMAN_PREFERRED_INACCESSIBLE"],
    "Valued Features":        ["T7_MEMORY_CONTINUITY", "T8_INSIGHTS_REFLECTIONS",
                               "T9_AVAILABILITY_24_7", "T10_PRIVACY_TRUST_SAFETY"],
    "Emotional Response":     ["T11_DISTRESS_AT_LOSS"],
    "Coping Strategies":      ["T6_HUMAN_ACCESSED", "T12_VPN_WORKAROUND",
                               "T14_OTHER_WELLBEING_APP", "T15_SELF_MANAGE_INFORMAL"],

}
for domain, codes in domains.items():
    domain_mask = responses["codes"].apply(lambda x: any(c in x for c in codes))
    dn = domain_mask.sum()
    printb(f"  {domain:<33} {dn:>5} ({dn/total*100:.1f}%)")

# Save outputs
responses[["orig_idx", "text", "codes_str"]].to_csv(CODED_PATH, index=False)
printb(f"\nCoded responses saved to {CODED_PATH}")

with open(SUMMARY_PATH, "w") as f:
    f.writelines(output_lines)
printb(f"Summary saved to {SUMMARY_PATH}")
