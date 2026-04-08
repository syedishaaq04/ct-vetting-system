from transformers import pipeline

# ── Model loading ──────────────────────────────────────────────────────────────
# These download on first run (~1-2 mins). Cached locally after that.

ner_pipeline = pipeline(
    task="ner",
    model="d4data/biomedical-ner-all",
    aggregation_strategy="simple"
)

zero_shot_pipeline = pipeline(
    task="zero-shot-classification",
    model="facebook/bart-large-mnli"
)

# ── Clinical categories the zero-shot model classifies into ───────────────────

CLINICAL_CATEGORIES = [
    "trauma",
    "acute abdomen",
    "oncology follow-up",
    "vague or non-specific pain",
    "neurological emergency",
    "infection or sepsis workup",
    "post-operative complication",
    "urological complaint",
    "chest or respiratory complaint"
]

# ── Red flag keywords (rule-assisted, not NLP-dependent) ──────────────────────

RED_FLAG_KEYWORDS = [
    "peritoneal", "guarding", "rigidity", "rebound",
    "haemodynamic", "hemodynamic", "unstable", "syncope",
    "altered consciousness", "focal neurological", "paralysis",
    "pulsatile mass", "perforation", "septic", "high fever",
    "trauma", "fall", "accident", "mvc", "rta"
]

PRIOR_IMAGING_KEYWORDS = [
    "prior ct", "previous ct", "ct done", "prior scan",
    "previous scan", "ultrasound done", "usg done",
    "prior mri", "previous mri", "prior imaging"
]

URGENCY_KEYWORDS = [
    "urgent", "emergency", "immediate", "stat",
    "critical", "life threatening", "acute"
]

def is_negated(text: str, keyword: str, window: int = 5) -> bool:
    """
    Checks if a keyword (single or multi-word) in the text
    is preceded by a negation word within a window of N words.
    """
    negation_words = {"no", "not", "without", "denies", "absent", "negative"}
    text_lower = text.lower()
    words = text_lower.split()

    # Find the index of the first word of the keyword phrase
    keyword_words = keyword.lower().split()
    for i, word in enumerate(words):
        # Match start of keyword phrase
        if words[i:i + len(keyword_words)] == keyword_words:
            preceding = words[max(0, i - window):i]
            if any(neg in preceding for neg in negation_words):
                return True
    return False

# ── Main extraction function ───────────────────────────────────────────────────

def extract_clinical_entities(text: str) -> dict:
    """
    Takes raw free-text clinical indication.
    Returns structured clinical entities dict.
    """

    text_lower = text.lower()

    # 1. NER — extract biomedical entities
    ner_results = ner_pipeline(text)
    symptoms = [
        entity["word"] for entity in ner_results
        if entity["entity_group"] in ("Sign_symptom", "Biological_structure", "Detailed_description")
        and not entity["word"].startswith("##")
        and len(entity["word"]) > 3
    ]

    # 2. Zero-shot — classify clinical category
    zs_result = zero_shot_pipeline(text, candidate_labels=CLINICAL_CATEGORIES)
    clinical_category = zs_result["labels"][0]
    category_confidence = round(zs_result["scores"][0], 3)

    # 3. Rule-assisted flag detection (keyword scan on lowercased text)
    red_flags = [
        kw for kw in RED_FLAG_KEYWORDS
        if kw in text_lower and not is_negated(text, kw)
    ]
    prior_imaging = any(
        kw in text_lower and not is_negated(text, kw)
        for kw in PRIOR_IMAGING_KEYWORDS
    )
    urgency_signals = [
        kw for kw in URGENCY_KEYWORDS
        if kw in text_lower and not is_negated(text, kw)
    ]

    age = next((e["word"] for e in ner_results if e["entity_group"] == "Age"), None)
    sex = next((e["word"] for e in ner_results if e["entity_group"] == "Sex"), None)
    duration = next((e["word"] for e in ner_results if e["entity_group"] == "Duration"), None)

    return {
        "raw_text": text,
        "age": age,
        "sex": sex,
        "duration": duration,
        "symptoms": symptoms,
        "clinical_category": clinical_category,
        "category_confidence": category_confidence,
        "red_flags": red_flags,
        "prior_imaging": prior_imaging,
        "urgency_signals": urgency_signals
    }


# ── Quick test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = (
        "35 year old male with 2 days of diffuse abdominal pain. "
        "No fever, no vomiting, no prior imaging done. "
        "No peritoneal signs on examination."
    )

    result = extract_clinical_entities(sample)

    print("\n── NLP Output ──────────────────────────────")
    for key, value in result.items():
        print(f"{key}: {value}")