# ── ACR-based scoring rules per clinical category ─────────────────────────────

SCORING_RULES = {
    "trauma": {
        "base_score": 7,
        "modifiers": {
            "high energy mechanism": +2,    # rta, mvc, fall from height
            "haemodynamically unstable": +2,
            "prior_imaging": -2,
            "urgency_signals": +1,
        },
        "thresholds": {"approve": 7, "flag": 4}
    },
    "acute abdomen": {
        "base_score": 6,
        "modifiers": {
            "red_flags": +3,
            "duration_over_72hrs": +1,
            "prior_imaging": +1,
            "urgency_signals": +1,
        },
        "thresholds": {"approve": 7, "flag": 4}
    },
    "vague or non-specific pain": {
        "base_score": 3,
        "modifiers": {
            "red_flags": +4,
            "duration_over_72hrs": +1,
            "prior_imaging": +2,
            "urgency_signals": +2,
        },
        "thresholds": {"approve": 7, "flag": 4}
    },
    "oncology follow-up": {
        "base_score": 7,
        "modifiers": {
            "prior_imaging": +1,
            "urgency_signals": +1,
        },
        "thresholds": {"approve": 6, "flag": 3}
    },
    "neurological emergency": {
        "base_score": 7,
        "modifiers": {
            "red_flags": +2,
            "urgency_signals": +2,
            "prior_imaging": +1,
        },
        "thresholds": {"approve": 6, "flag": 4}
    },
    "infection or sepsis workup": {
        "base_score": 5,
        "modifiers": {
            "red_flags": +3,
            "urgency_signals": +2,
            "duration_over_72hrs": +1,
            "prior_imaging": +1,
        },
        "thresholds": {"approve": 7, "flag": 4}
    },
    "post-operative complication": {
        "base_score": 6,
        "modifiers": {
            "red_flags": +3,
            "urgency_signals": +2,
            "prior_imaging": +1,
        },
        "thresholds": {"approve": 6, "flag": 4}
    },
    "urological complaint": {
        "base_score": 4,
        "modifiers": {
            "red_flags": +3,
            "duration_over_72hrs": +1,
            "prior_imaging": +2,
            "urgency_signals": +2,
        },
        "thresholds": {"approve": 7, "flag": 4}
    },
    "chest or respiratory complaint": {
        "base_score": 5,
        "modifiers": {
            "red_flags": +3,
            "urgency_signals": +2,
            "prior_imaging": +1,
            "duration_over_72hrs": +1,
        },
        "thresholds": {"approve": 7, "flag": 4}
    }
}

# ── Fallback for any category the zero-shot returns that isn't mapped ──────────

DEFAULT_RULE = {
    "base_score": 4,
    "modifiers": {
        "red_flags": +3,
        "urgency_signals": +2,
        "prior_imaging": +1,
        "duration_over_72hrs": +1,
    },
    "thresholds": {"approve": 7, "flag": 4}
}

# ── Alternatives to suggest on reject/flag ────────────────────────────────────

ALTERNATIVES = {
    "vague or non-specific pain": "Consider ultrasound abdomen as first-line imaging.",
    "urological complaint": "Consider ultrasound KUB before CT.",
    "chest or respiratory complaint": "Consider chest X-ray before CT thorax.",
    "neurological emergency": "Consider MRI brain if non-urgent neurological complaint.",
    "infection or sepsis workup": "Consider clinical evaluation and labs before advanced imaging.",
    "trauma": None,
    "acute abdomen": None,
    "oncology follow-up": None,
    "post-operative complication": None,
}


# ── Duration parser ───────────────────────────────────────────────────────────

def is_duration_over_72hrs(duration_str: str) -> bool:
    """
    Parses duration string from NLP and checks if it exceeds 72 hours.
    Handles formats like: '2 days', '4 hours', '1 week', '3 months'
    """
    if not duration_str:
        return False

    duration_lower = duration_str.lower()

    if "week" in duration_lower or "month" in duration_lower or "year" in duration_lower:
        return True

    if "day" in duration_lower:
        try:
            days = float(''.join(filter(lambda x: x.isdigit() or x == '.', duration_lower)))
            return days >= 3
        except ValueError:
            return False

    if "hour" in duration_lower:
        try:
            hours = float(''.join(filter(lambda x: x.isdigit() or x == '.', duration_lower)))
            return hours >= 72
        except ValueError:
            return False

    return False


# ── Main scoring function ──────────────────────────────────────────────────────

def compute_score(nlp_output: dict) -> dict:
    """
    Takes NLP output dict.
    Returns score (0-10), verdict, and alternative suggestion.
    """

    category = nlp_output.get("clinical_category", "").lower()
    rule = SCORING_RULES.get(category, DEFAULT_RULE)

    score = rule["base_score"]
    modifiers = rule["modifiers"]
    applied_modifiers = []

    # Apply modifiers
    if nlp_output.get("red_flags") and "red_flags" in modifiers:
        score += modifiers["red_flags"]
        applied_modifiers.append(f"red flags present: +{modifiers['red_flags']}")

    if nlp_output.get("prior_imaging") and "prior_imaging" in modifiers:
        score += modifiers["prior_imaging"]
        applied_modifiers.append(f"prior imaging done: +{modifiers['prior_imaging']}")

    if nlp_output.get("urgency_signals") and "urgency_signals" in modifiers:
        score += modifiers["urgency_signals"]
        applied_modifiers.append(f"urgency signals present: +{modifiers['urgency_signals']}")

    if is_duration_over_72hrs(nlp_output.get("duration", "")) and "duration_over_72hrs" in modifiers:
        score += modifiers["duration_over_72hrs"]
        applied_modifiers.append(f"duration over 72hrs: +{modifiers['duration_over_72hrs']}")

    # Clamp score between 0 and 10
    score = max(0, min(10, score))

    # Verdict
    thresholds = rule["thresholds"]
    if score >= thresholds["approve"]:
        verdict = "APPROVE"
    elif score >= thresholds["flag"]:
        verdict = "FLAG FOR REVIEW"
    else:
        verdict = "SOFT REJECT"

    alternative = ALTERNATIVES.get(category)

    return {
        "score": round(score, 1),
        "verdict": verdict,
        "category": category,
        "base_score": rule["base_score"],
        "applied_modifiers": applied_modifiers,
        "alternative": alternative
    }


# ── Quick test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_nlp_output = {
    "clinical_category": "vague or non-specific pain",
    "red_flags": ["guarding", "rigidity"],
    "prior_imaging": True,
    "urgency_signals": ["urgent"],
    "duration": "4 days"
    }

    result = compute_score(sample_nlp_output)

    print("\n── Scoring Output ──────────────────────────")
    for key, value in result.items():
        print(f"{key}: {value}")