#!/usr/bin/env python3
"""
CT Scan Vetting Engine - Main Integration Module

This module integrates the NLP pipeline, scoring engine, and LLM layer
to provide a complete CT scan vetting solution for radiologists.

Usage:
    from vetting_engine import VettingEngine
    
    engine = VettingEngine()
    result = engine.vet_request("35 year old male with 2 days of abdominal pain...")
"""

import json
import sys
from pathlib import Path

# Add core directory to path for imports
sys.path.append(str(Path(__file__).parent / "core"))

try:
    from core.nlp_pipeline import extract_clinical_entities
    from core.scoring_engine import compute_score
    from core.llm_layer import generate_justification
except ImportError as e:
    print(f"Error importing core modules: {e}")
    print("Make sure all core modules are present in the 'core' directory.")
    sys.exit(1)


class VettingEngine:
    """
    Main CT scan vetting engine that orchestrates NLP processing,
    scoring, and LLM justification generation.
    """
    
    def __init__(self):
        """Initialize the vetting engine."""
        self.version = "1.0.0"
    
    def vet_request(self, clinical_text: str) -> dict:
        """
        Process a CT scan vetting request through the complete pipeline.
        
        Args:
            clinical_text (str): Raw clinical indication text
            
        Returns:
            dict: Complete vetting result with NLP, scoring, and justification
        """
        try:
            # Step 1: NLP Processing
            nlp_result = extract_clinical_entities(clinical_text)
            
            # Step 2: Scoring Engine
            scoring_result = compute_score(nlp_result)
            
            # Step 3: LLM Justification
            justification_result = generate_justification(nlp_result, scoring_result)
            
            # Combine all results
            final_result = {
                "input": {
                    "clinical_text": clinical_text,
                    "text_length": len(clinical_text)
                },
                "nlp_processing": {
                    "status": "completed",
                    "extracted_entities": nlp_result
                },
                "scoring": {
                    "status": "completed", 
                    "score_analysis": scoring_result
                },
                "justification": {
                    "status": "completed",
                    "llm_output": justification_result
                },
                "final_decision": {
                    "verdict": scoring_result["verdict"],
                    "score": scoring_result["score"],
                    "category": scoring_result["category"],
                    "requires_review": scoring_result["verdict"] in ["FLAG FOR REVIEW", "SOFT REJECT"],
                    "alternative_imaging": scoring_result["alternative"]
                },
                "processing_metadata": {
                    "engine_version": self.version,
                    "pipeline_stages": ["nlp_processing", "scoring", "justification"],
                    "all_stages_completed": True
                }
            }
            
            return final_result
            
        except Exception as e:
            # Return error result if any stage fails
            return {
                "input": {
                    "clinical_text": clinical_text,
                    "text_length": len(clinical_text)
                },
                "error": {
                    "message": str(e),
                    "type": type(e).__name__,
                    "stage": "pipeline_processing"
                },
                "processing_metadata": {
                    "engine_version": self.version,
                    "pipeline_stages": ["nlp_processing", "scoring", "justification"],
                    "all_stages_completed": False
                }
            }
    
    def get_summary_report(self, vetting_result: dict) -> str:
        """
        Generate a human-readable summary report from vetting results.
        
        Args:
            vetting_result (dict): Result from vet_request()
            
        Returns:
            str: Formatted summary report
        """
        if "error" in vetting_result:
            return f"ERROR: {vetting_result['error']['message']}"
        
        decision = vetting_result["final_decision"]
        nlp_data = vetting_result["nlp_processing"]["extracted_entities"]
        scoring_data = vetting_result["scoring"]["score_analysis"]
        justification = vetting_result["justification"]["llm_output"]
        
        report = f"""
CT SCAN VETTING REPORT
{'='*50}

CLINICAL INPUT:
{nlp_data.get('raw_text', 'Not provided')}

EXTRACTED INFORMATION:
- Age: {nlp_data.get('age', 'Unknown')}
- Sex: {nlp_data.get('sex', 'Unknown')}
- Duration: {nlp_data.get('duration', 'Unknown')}
- Symptoms: {', '.join(nlp_data.get('symptoms', [])) or 'None'}
- Clinical Category: {nlp_data.get('clinical_category', 'Unknown')}
- Red Flags: {', '.join(nlp_data.get('red_flags', [])) or 'None'}
- Prior Imaging: {nlp_data.get('prior_imaging', False)}

SCORING ANALYSIS:
- Base Score: {scoring_data.get('base_score', 'N/A')}
- Final Score: {scoring_data.get('score', 'N/A')}/10
- Verdict: {decision['verdict']}
- Applied Modifiers: {', '.join(scoring_data.get('applied_modifiers', [])) or 'None'}

FINAL DECISION:
{decision['verdict']} - Score: {decision['score']}/10
Requires Review: {'Yes' if decision['requires_review'] else 'No'}
Alternative Imaging: {decision['alternative_imaging'] or 'None'}

AI JUSTIFICATION:
Summary: {justification.get('summary', 'Not available')}
Reasoning: {justification.get('reasoning', 'Not available')}
Red Flags to Watch: {', '.join(justification.get('red_flags_to_watch', [])) or 'None'}

{'='*50}
"""
        return report.strip()


def main():
    """
    Command-line interface for the vetting engine.
    """
    print("CT Scan Vetting Engine - CLI Mode")
    print("=" * 40)
    
    engine = VettingEngine()
    
    # Get input from user
    print("\nEnter clinical indication (or 'quit' to exit):")
    while True:
        clinical_text = input("\n> ").strip()
        
        if clinical_text.lower() in ['quit', 'exit', 'q']:
            print("Exiting vetting engine.")
            break
        
        if not clinical_text:
            print("Please enter a clinical indication.")
            continue
        
        print("\nProcessing...")
        result = engine.vet_request(clinical_text)
        
        # Display summary report
        print(engine.get_summary_report(result))
        
        # Ask if user wants to see full JSON
        show_json = input("\nShow full JSON output? (y/n): ").lower()
        if show_json in ['y', 'yes']:
            print("\nFull JSON Result:")
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()