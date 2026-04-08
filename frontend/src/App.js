import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [clinicalText, setClinicalText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  // Sample clinical inputs for testing
  const sampleInputs = [
    {
      name: "Acute Trauma",
      text: "45 year old male involved in high-speed MVC, complaints of abdominal pain and tenderness, haemodynamically unstable, emergency CT requested."
    },
    {
      name: "Vague Pain",
      text: "35 year old female with 2 days of diffuse abdominal pain, no fever, no vomiting, no prior imaging done, no peritoneal signs on examination."
    },
    {
      name: "Acute Abdomen",
      text: "60 year old male with 4 days of worsening abdominal pain, guarding and rigidity on examination, high fever, peritoneal signs present."
    },
    {
      name: "Urological",
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
      const response = await axios.post('http://localhost:8000/vet', {
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
      case 'APPROVE': return 'approve';
      case 'FLAG FOR REVIEW': return 'flag';
      case 'SOFT REJECT': return 'reject';
      default: return '';
    }
  };

  const getScoreClass = (score) => {
    if (score >= 7) return 'high';
    if (score >= 4) return 'medium';
    return 'low';
  };

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
  const hasText = clinicalText.trim().length > 0;
  const hasResults = Boolean(results && finalDecision && extractedEntities && scoringAnalysis && justification);

  return (
    <div className="App">
      <div className="app-shell">
        <header className="hero">
          <div className="hero-copy">
            <span className="eyebrow">AI-assisted radiology workflow</span>
            <h1>CT Scan Vetting System</h1>
            <p>
              A polished clinical triage interface for reviewing CT requests with
              fast NLP extraction, rule-based scoring, and AI justification.
            </p>
            <div className="hero-pills" aria-label="Product highlights">
              <span>NLP extraction</span>
              <span>Rule-based scoring</span>
              <span>LLM justification</span>
            </div>
          </div>

          <div className="hero-panel">
            <div className={`hero-status ${hasResults ? 'is-ready' : hasText ? 'is-primed' : 'is-idle'}`}>
              <span className="status-dot"></span>
              <span>{hasResults ? 'Analysis complete' : hasText ? 'Request prepared' : 'Waiting for input'}</span>
            </div>
            <div className="hero-metric">
              <span className="metric-label">Status</span>
              <span className="metric-value">Live demo</span>
            </div>
            <div className="hero-metric">
              <span className="metric-label">Pipeline</span>
              <span className="metric-value">NLP + Scoring + LLM</span>
            </div>
            <div className="hero-metric">
              <span className="metric-label">Audience</span>
              <span className="metric-value">Radiology triage</span>
            </div>
          </div>
        </header>

        <main className="dashboard-grid">
          <section className="panel panel-primary">
            <div className="panel-header">
              <div>
                <span className="panel-kicker">Clinical input</span>
                <h2>Enter request details</h2>
              </div>
              <button type="button" className="ghost-button" onClick={handleClear} disabled={loading && !clinicalText}>
                Reset
              </button>
            </div>

            <div className="sample-inputs">
              <div className="section-title-row">
                <h3>Quick sample inputs</h3>
                <span>One-click clinical scenarios</span>
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
                    <span>Load example text</span>
                  </button>
                ))}
              </div>
            </div>

            <form className="vetting-form" onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="clinical-text">Clinical indication</label>
                <textarea
                  id="clinical-text"
                  value={clinicalText}
                  onChange={(e) => setClinicalText(e.target.value)}
                  placeholder="Enter the clinical indication for CT scan..."
                  disabled={loading}
                  spellCheck="false"
                />
                <div className="char-count">{clinicalText.length} characters</div>
              </div>

              {error && <div className="error">{error}</div>}

              <div className="button-row">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading || !clinicalText.trim()}
                >
                  {loading ? 'Analyzing...' : 'Analyze request'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleClear}
                  disabled={loading}
                >
                  Clear text
                </button>
              </div>
            </form>

            {loading && (
              <div className="loading loading-card">
                <div className="spinner"></div>
                <div>
                  <strong>Analyzing request</strong>
                  <span>Clinical signal extraction and scoring in progress</span>
                </div>
              </div>
            )}
          </section>

          <aside className="panel panel-side">
            <div className="panel-header">
              <div>
                <span className="panel-kicker">At a glance</span>
                <h2>Clinical workflow</h2>
              </div>
            </div>

            <div className="workflow-card">
              <div className="workflow-step">
                <span className="step-index">1</span>
                <div>
                  <h3>Extract entities</h3>
                  <p>Age, symptoms, urgency, and red flags from free text.</p>
                </div>
              </div>
              <div className="workflow-step">
                <span className="step-index">2</span>
                <div>
                  <h3>Apply score</h3>
                  <p>Rule-based necessity scoring aligned to clinical category.</p>
                </div>
              </div>
              <div className="workflow-step">
                <span className="step-index">3</span>
                <div>
                  <h3>Generate justification</h3>
                  <p>Provide concise reasoning and alternative imaging if needed.</p>
                </div>
              </div>
            </div>

            <div className="info-card">
              <span className="info-card-label">Design intent</span>
              <p>
                Clean hierarchy, high contrast, and subtle gradients keep the
                interface readable in a clinical demo setting.
              </p>
              <div className="info-note">
                Built for quick review, calm reading, and a strong presentation on stage.
              </div>
            </div>
          </aside>
        </main>

        {hasResults && (
          <section className="results">
            <div className={`results-header ${getVerdictClass(finalDecision.verdict)}`}>
              <div className="results-header-top">
                <div>
                  <span className="panel-kicker">Decision summary</span>
                  <h2>Vetting results</h2>
                </div>
                <div className={`verdict-badge ${getVerdictClass(finalDecision.verdict)}`}>
                  {finalDecision.verdict}
                </div>
              </div>

              <div className="results-ribbon">
                <div className="results-ribbon-item">
                  <span>Score band</span>
                  <strong>{finalDecision.score >= 7 ? 'Appropriate' : finalDecision.score >= 4 ? 'Review' : 'Low priority'}</strong>
                </div>
                <div className="results-ribbon-item">
                  <span>Confidence</span>
                  <strong>{formatConfidence(confidenceValue)}</strong>
                </div>
                <div className="results-ribbon-item">
                  <span>Pipeline</span>
                  <strong>Complete</strong>
                </div>
              </div>

              <div className="decision-surface">
                <div className="decision-score">
                  <span>Score</span>
                  <strong>{finalDecision.score}/10</strong>
                </div>
                <div className="decision-meta">
                  <div>
                    <span>Category</span>
                    <strong>{finalDecision.category}</strong>
                  </div>
                  <div>
                    <span>Requires review</span>
                    <strong>{finalDecision.requires_review ? 'Yes' : 'No'}</strong>
                  </div>
                  <div>
                    <span>Category confidence</span>
                    <strong>{formatConfidence(confidenceValue)}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div className="results-content">
              <div className="result-section">
                <h3>Final decision</h3>
                <div className="result-grid result-grid-compact">
                  <div className="result-item emphasis">
                    <strong>Verdict</strong>
                    <span className={`verdict-badge ${getVerdictClass(finalDecision.verdict)}`}>
                      {finalDecision.verdict}
                    </span>
                  </div>
                  <div className="result-item emphasis">
                    <strong>Score</strong>
                    <div className={`score-display ${getScoreClass(finalDecision.score)}`}>
                      {finalDecision.score}/10
                    </div>
                  </div>
                  <div className="result-item">
                    <strong>Category</strong>
                    {finalDecision.category}
                  </div>
                  <div className="result-item">
                    <strong>Requires review</strong>
                    {finalDecision.requires_review ? 'Yes' : 'No'}
                  </div>
                </div>

                {finalDecision.alternative_imaging && (
                  <div className="alternative-imaging">
                    <strong>Alternative imaging</strong>
                    <span>{finalDecision.alternative_imaging}</span>
                  </div>
                )}
              </div>

              <div className="results-two-column">
                <div className="result-section card-surface">
                  <h3>Extracted clinical information</h3>
                  <div className="result-grid">
                    <div className="result-item"><strong>Age</strong>{extractedEntities.age || 'Not detected'}</div>
                    <div className="result-item"><strong>Sex</strong>{extractedEntities.sex || 'Not detected'}</div>
                    <div className="result-item"><strong>Duration</strong>{extractedEntities.duration || 'Not detected'}</div>
                    <div className="result-item"><strong>Clinical category</strong>{extractedEntities.clinical_category}</div>
                    <div className="result-item"><strong>Prior imaging</strong>{extractedEntities.prior_imaging ? 'Yes' : 'No'}</div>
                    <div className="result-item"><strong>Category confidence</strong>{formatConfidence(confidenceValue)}</div>
                  </div>

                  {extractedEntities.symptoms.length > 0 && (
                    <div className="result-block">
                      <strong>Symptoms</strong>
                      <ul className="tag-list">
                        {extractedEntities.symptoms.map((symptom, index) => (
                          <li key={index}>{symptom}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {extractedEntities.red_flags.length > 0 && (
                    <div className="result-block">
                      <strong>Red flags</strong>
                      <ul className="tag-list tag-list-danger">
                        {extractedEntities.red_flags.map((flag, index) => (
                          <li key={index}>{flag}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                <div className="result-section card-surface">
                  <h3>Scoring analysis</h3>
                  <div className="result-grid result-grid-tight">
                    <div className="result-item"><strong>Base score</strong>{scoringAnalysis.base_score}</div>
                    <div className="result-item"><strong>Final score</strong>{scoringAnalysis.score}/10</div>
                    <div className="result-item result-item-wide">
                      <strong>Applied modifiers</strong>
                      {scoringAnalysis.applied_modifiers.length > 0 ? scoringAnalysis.applied_modifiers.join(', ') : 'None'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="result-section justification-section">
                <h3>AI justification</h3>
                <div className="justification-box">
                  <div className="justification-summary">
                    <span>Summary</span>
                    <p>{justification.summary}</p>
                  </div>
                  <div className="justification-summary">
                    <span>Reasoning</span>
                    <p>{justification.reasoning}</p>
                  </div>

                  {justification.red_flags_to_watch.length > 0 && (
                    <div className="justification-summary">
                      <span>Red flags to watch</span>
                      <ul className="tag-list tag-list-neutral">
                        {justification.red_flags_to_watch.map((flag, index) => (
                          <li key={index}>{flag}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
