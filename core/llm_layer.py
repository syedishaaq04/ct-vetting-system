import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a clinical decision support assistant embedded in a CT scan vetting system 
used by radiologists in high-volume hospitals.

Your role is to generate a clear, concise, evidence-based justification for a 
vetting decision that has already been made by the scoring engine.

Rules you must follow:
- Never override the verdict or score given to you.
- Never make a diagnosis.
- Never recommend a specific treatment.
- Always recommend an alternative imaging modality when verdict is SOFT REJECT or FLAG FOR REVIEW.
- Keep reasoning concise — 2 to 3 sentences maximum.
- Always respond in valid JSON only. No preamble. No markdown. No explanation outside the JSON.

Your response must follow this exact structure:
{
  "summary": "One-line clinical summary of the request",
  "reasoning": "2-3 sentence evidence-based justification for the verdict",
  "alternative": "Suggested alternative if verdict is not APPROVE, else null",
  "red_flags_to_watch": ["list", "of", "signs", "that", "would", "upgrade", "urgency"]
}
"""

# ── Dynamic user prompt builder ───────────────────────────────────────────────

def build_prompt(nlp_output: dict, scoring_output: dict) -> str:
    return f"""
CT Scan Vetting Request:

Raw clinical indication: {nlp_output.get('raw_text', 'Not provided')}

Extracted clinical entities:
- Age: {nlp_output.get('age', 'Unknown')}
- Sex: {nlp_output.get('sex', 'Unknown')}
- Duration: {nlp_output.get('duration', 'Unknown')}
- Symptoms: {', '.join(nlp_output.get('symptoms', [])) or 'None extracted'}
- Red flags: {', '.join(nlp_output.get('red_flags', [])) or 'None'}
- Prior imaging: {nlp_output.get('prior_imaging', False)}
- Urgency signals: {', '.join(nlp_output.get('urgency_signals', [])) or 'None'}

Scoring engine output:
- Clinical category: {scoring_output.get('category', 'Unknown')}
- Necessity score: {scoring_output.get('score')}/10
- Verdict: {scoring_output.get('verdict')}
- Applied modifiers: {', '.join(scoring_output.get('applied_modifiers', [])) or 'None'}
- Suggested alternative: {scoring_output.get('alternative') or 'None'}

Generate the JSON justification for this vetting decision.
"""

# ── Main LLM call ─────────────────────────────────────────────────────────────

def generate_justification(nlp_output: dict, scoring_output: dict) -> dict:
    """
    Takes NLP output and scoring output.
    Returns LLM-generated justification as a dict.
    """
    prompt = build_prompt(nlp_output, scoring_output)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if model adds them despite instructions
        if raw.startswith("```"):
            # Handle both ```json and ``` formats
            if raw.startswith("```json"):
                raw = raw[7:]  # Remove ```json prefix
            elif raw.startswith("```"):
                raw = raw[3:]  # Remove ``` prefix
            
            # Remove closing ``` if present
            if raw.endswith("```"):
                raw = raw[:-3]
            
            # Handle case where there's a newline after opening fence
            if raw.startswith("\n"):
                raw = raw[1:]
            if raw.endswith("\n"):
                raw = raw[:-1]
        
        raw = raw.strip()

        import json
        return json.loads(raw)

    except Exception as e:
        return {
            "summary": "LLM justification unavailable",
            "reasoning": str(e),
            "alternative": scoring_output.get("alternative"),
            "red_flags_to_watch": []
        }


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_nlp = {
        "raw_text": "35 year old male with 2 days of diffuse abdominal pain. No fever, no vomiting, no prior imaging done. No peritoneal signs on examination.",
        "age": "35 year old",
        "sex": "male",
        "duration": "2 days",
        "symptoms": ["diffuse", "abdominal", "pain"],
        "red_flags": [],
        "prior_imaging": False,
        "urgency_signals": []
    }

    sample_scoring = {
        "score": 3,
        "verdict": "SOFT REJECT",
        "category": "vague or non-specific pain",
        "base_score": 3,
        "applied_modifiers": [],
        "alternative": "Consider ultrasound abdomen as first-line imaging."
    }

    result = generate_justification(sample_nlp, sample_scoring)

    print("\n── LLM Output ──────────────────────────────")
    import json
    print(json.dumps(result, indent=2))