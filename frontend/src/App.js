import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [clinicalText, setClinicalText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const apiBase = 'http://localhost:8000';

  // Sample clinical inputs for testing
  const sampleInputs = [
    {
      name: "Acute Trauma",
      hint: "High-risk mechanism with instability",
      text: "45 year old male involved in high-speed MVC, complaints of abdominal pain and tenderness, haemodynamically unstable, emergency CT requested."
    },
    {
      name: "Vague Pain",
      hint: "Low-specificity abdominal symptoms",
      text: "35 year old female with 2 days of diffuse abdominal pain, no fever, no vomiting, no prior imaging done, no peritoneal signs on examination."
    },
    {
      name: "Acute Abdomen",
      hint: "Peritoneal signs and high fever",
      text: "60 year old male with 4 days of worsening abdominal pain, guarding and rigidity on examination, high fever, peritoneal signs present."
    },
    {
      name: "Urological",
      hint: "Flank pain with hematuria",
      text: "40 year old male with right flank pain and hematuria for 1 day, no prior imaging, urgent evaluation requested."
    }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!clinicalText.trim() || clinicalText.length < 10) {
      setError('Please enter at least 10 characters of clinical text.');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post(`${apiBase}/vet`, {
        clinical_text: clinicalText
      });

      if (response.data.success) {
        setResults(response.data.data);
      } else {
        setError(response.data.error || 'An error occurred during processing.');
      }
    } catch (err) {
      setError('Failed to connect to the server. Please make sure the API is running on localhost:8000');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setClinicalText('');
    setResults(null);
    setError('');
  };

  const loadSample = (sampleText) => {
    setClinicalText(sampleText);
    setError('');
  };

  const getVerdictClass = (verdict) => {
    switch (verdict) {
      case 'APPROVE': return 'tone-approve';
      case 'FLAG FOR REVIEW': return 'tone-flag';
      case 'SOFT REJECT': return 'tone-reject';
      default: return 'tone-default';
    }
  };

  const asArray = (value) => (Array.isArray(value) ? value : []);

  const formatConfidence = (value) => {
    if (value === null || value === undefined || value === '') {
      return 'Not available';
    }

    const numericValue = Number(value);
    if (Number.isNaN(numericValue)) {
      return String(value);
    }

    return `${Math.round(numericValue * 100)}%`;
  };

  const confidenceValue = results ? results.nlp_processing.extracted_entities.category_confidence : null;
  const finalDecision = results ? results.final_decision : null;
  const extractedEntities = results ? results.nlp_processing.extracted_entities : null;
  const scoringAnalysis = results ? results.scoring.score_analysis : null;
  const justification = results ? results.justification.llm_output : null;
  const processingMeta = results ? results.processing_metadata : null;

  const symptoms = asArray(extractedEntities?.symptoms);
  const redFlags = asArray(extractedEntities?.red_flags);
  const urgencySignals = asArray(extractedEntities?.urgency_signals);
  const appliedModifiers = asArray(scoringAnalysis?.applied_modifiers);
  const redFlagsToWatch = asArray(justification?.red_flags_to_watch);

  const textLength = clinicalText.trim().length;
  const hasText = textLength > 0;
  const hasResults = Boolean(results && finalDecision && extractedEntities && scoringAnalysis && justification);
  const textReadiness = Math.max(0, Math.min(100, Math.round((textLength / 220) * 100)));
  const scoreValue = Number(finalDecision?.score ?? 0);
  const scorePercent = Math.max(0, Math.min(100, Math.round(scoreValue * 10)));

  return (
    <div className="App">
      <div className="ambient ambient-a"></div>
      <div className="ambient ambient-b"></div>

      <div className="layout-shell">
        <header className="top-banner">
          <div className="banner-title-group">
            <span className="eyebrow">Clinical command center</span>
            <h1>CT Vetting Studio</h1>
            <p>
              A complete triage workspace for radiology request screening with
              entity extraction, clinical scoring, and AI-generated rationale.
            </p>
          </div>

          <div className="banner-chip-row" aria-label="Platform capabilities">
            <span className="capability-chip">Biomedical NLP</span>
            <span className="capability-chip">ACR-aligned scoring</span>
            <span className="capability-chip">Structured justification</span>
          </div>
        </header>

        <section className="hero-grid">
          <article className="hero-card">
            <div className="hero-card-head">
              <span className="panel-kicker">Live status</span>
              <div className={`status-pill ${hasResults ? 'is-ready' : hasText ? 'is-primed' : 'is-idle'}`}>
                <span className="status-dot"></span>
                <span>{hasResults ? 'Analysis complete' : hasText ? 'Request drafted' : 'Awaiting request text'}</span>
              </div>
            </div>

            <div className="hero-metrics">
              <div className="metric-card">
                <span className="metric-label">API endpoint</span>
                <strong className="metric-value">{apiBase}</strong>
              </div>
              <div className="metric-card">
                <span className="metric-label">Pipeline stages</span>
                <strong className="metric-value">NLP · Score · LLM</strong>
              </div>
              <div className="metric-card">
                <span className="metric-label">Input readiness</span>
                <strong className="metric-value">{textReadiness}%</strong>
              </div>
            </div>

            <div className="readiness-meter" style={{ '--fill': `${textReadiness}%` }}>
              <span>Text readiness</span>
              <div className="readiness-track">
                <div className="readiness-bar"></div>
              </div>
            </div>
          </article>

          <aside className="guide-card">
            <span className="panel-kicker">How it works</span>
            <h2>Clinical reasoning flow</h2>
            <div className="flow-list">
              <div className="flow-item">
                <span className="flow-index">01</span>
                <div>
                  <h3>Extract entities</h3>
                  <p>Captures age, sex, symptoms, urgency signals, and red flags from free text.</p>
                </div>
              </div>
              <div className="flow-item">
                <span className="flow-index">02</span>
                <div>
                  <h3>Score necessity</h3>
                  <p>Applies category-specific base scores plus evidence-based modifiers.</p>
                </div>
              </div>
              <div className="flow-item">
                <span className="flow-index">03</span>
                <div>
                  <h3>Produce rationale</h3>
                  <p>Generates concise justification and safety-oriented red flags to watch.</p>
                </div>
              </div>
            </div>
          </aside>
        </section>

        <main className="workspace-grid">
          <section className="panel panel-main">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">Request composer</span>
                <h2>Clinical indication input</h2>
              </div>
              <button type="button" className="ghost-button" onClick={handleClear} disabled={loading && !hasText}>
                Reset form
              </button>
            </div>

            <div className="sample-library">
              <div className="section-headline">
                <h3>Scenario templates</h3>
                <span>Prefill realistic cases for demos and validation.</span>
              </div>
              <div className="sample-grid">
                {sampleInputs.map((sample, index) => (
                  <button
                    key={index}
                    type="button"
                    className="sample-btn"
                    onClick={() => loadSample(sample.text)}
                  >
                    <strong>{sample.name}</strong>
                    <span>{sample.hint}</span>
                  </button>
                ))}
              </div>
            </div>

            <form className="composer-form" onSubmit={handleSubmit}>
              <label htmlFor="clinical-text" className="input-label">Clinical indication text</label>
              <textarea
                id="clinical-text"
                value={clinicalText}
                onChange={(e) => setClinicalText(e.target.value)}
                placeholder="Enter detailed clinical context, symptoms, duration, red flags, and urgency indicators..."
                disabled={loading}
                spellCheck="false"
              />
              <div className="field-meta-row">
                <span>{textLength} characters</span>
                <span>Minimum recommended: 30+</span>
              </div>

              {error && <div className="error-banner">{error}</div>}

              <div className="action-row">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading || !hasText}
                >
                  {loading ? 'Analyzing request...' : 'Run vetting analysis'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleClear}
                  disabled={loading}
                >
                  Clear
                </button>
              </div>
            </form>

            {loading && (
              <div className="loading-panel">
                <div className="spinner"></div>
                <div>
                  <strong>Pipeline running</strong>
                  <span>Entity extraction, scoring, and justification are in progress.</span>
                </div>
              </div>
            )}

            {!hasResults && !loading && (
              <div className="empty-state">
                <h3>Ready for analysis</h3>
                <p>
                  Submit a clinical request to generate a triage verdict,
                  confidence snapshot, and evidence-backed AI reasoning.
                </p>
              </div>
            )}
          </section>

          <aside className="panel panel-side">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">Operator panel</span>
                <h2>Session context</h2>
              </div>
            </div>

            <div className="context-list">
              <div className="context-item">
                <span>Backend</span>
                <strong>localhost:8000</strong>
              </div>
              <div className="context-item">
                <span>Frontend</span>
                <strong>localhost:3000</strong>
              </div>
              <div className="context-item">
                <span>Readiness score</span>
                <strong>{textReadiness}%</strong>
              </div>
              <div className="context-item">
                <span>Current phase</span>
                <strong>{loading ? 'Running analysis' : hasResults ? 'Result ready' : 'Awaiting submission'}</strong>
              </div>
            </div>

            <div className="note-block">
              <span className="panel-kicker">Clinical safety note</span>
              <p>
                This tool supports prioritization decisions. Final clinical judgment
                remains with qualified radiology and emergency teams.
              </p>
            </div>
          </aside>
        </main>

        {hasResults && (
          <section className={`result-board ${getVerdictClass(finalDecision.verdict)}`}>
            <div className="result-hero">
              <div className="result-headline">
                <span className="panel-kicker">Vetting outcome</span>
                <h2>{finalDecision.verdict}</h2>
                <p>
                  Category: <strong>{finalDecision.category}</strong>
                </p>
              </div>

              <div className="score-ring" style={{ '--score-fill': `${scorePercent}%` }}>
                <div className="score-core">
                  <span>Score</span>
                  <strong>{scoreValue}/10</strong>
                </div>
              </div>
            </div>

            <div className="snapshot-grid">
              <div className="snapshot-card">
                <span>Category confidence</span>
                <strong>{formatConfidence(confidenceValue)}</strong>
              </div>
              <div className="snapshot-card">
                <span>Requires review</span>
                <strong>{finalDecision.requires_review ? 'Yes' : 'No'}</strong>
              </div>
              <div className="snapshot-card">
                <span>Processing stages</span>
                <strong>{asArray(processingMeta?.pipeline_stages).join(' -> ') || 'NLP -> Scoring -> LLM'}</strong>
              </div>
            </div>

            <div className="result-columns">
              <article className="glass-card">
                <h3>Extracted entities</h3>
                <div className="detail-grid">
                  <div><span>Age</span><strong>{extractedEntities.age || 'Not detected'}</strong></div>
                  <div><span>Sex</span><strong>{extractedEntities.sex || 'Not detected'}</strong></div>
                  <div><span>Duration</span><strong>{extractedEntities.duration || 'Not detected'}</strong></div>
                  <div><span>Prior imaging</span><strong>{extractedEntities.prior_imaging ? 'Yes' : 'No'}</strong></div>
                </div>

                <div className="chip-group-block">
                  <span>Symptoms</span>
                  <ul className="chip-list">
                    {(symptoms.length > 0 ? symptoms : ['No symptoms extracted']).map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="chip-group-block">
                  <span>Urgency signals</span>
                  <ul className="chip-list chip-list-neutral">
                    {(urgencySignals.length > 0 ? urgencySignals : ['None detected']).map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="chip-group-block">
                  <span>Red flags</span>
                  <ul className="chip-list chip-list-danger">
                    {(redFlags.length > 0 ? redFlags : ['No red flags detected']).map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>
              </article>

              <article className="glass-card">
                <h3>Scoring and recommendation</h3>
                <div className="detail-grid detail-grid-compact">
                  <div><span>Base score</span><strong>{scoringAnalysis.base_score}</strong></div>
                  <div><span>Final score</span><strong>{scoringAnalysis.score}/10</strong></div>
                </div>

                <div className="chip-group-block">
                  <span>Applied modifiers</span>
                  <ul className="chip-list chip-list-accent">
                    {(appliedModifiers.length > 0 ? appliedModifiers : ['No modifiers applied']).map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="justification-card">
                  <span>Summary</span>
                  <p>{justification.summary || 'No summary available.'}</p>

                  <span>Reasoning</span>
                  <p>{justification.reasoning || 'No reasoning available.'}</p>

                  <span>Red flags to watch</span>
                  <ul className="chip-list chip-list-neutral">
                    {(redFlagsToWatch.length > 0 ? redFlagsToWatch : ['None provided']).map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>

                {finalDecision.alternative_imaging && (
                  <div className="alt-imaging-card">
                    <span>Alternative imaging</span>
                    <strong>{finalDecision.alternative_imaging}</strong>
                  </div>
                )}
              </article>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
