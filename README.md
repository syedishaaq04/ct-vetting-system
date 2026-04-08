# CT Scan Vetting System

**MVP for College Tech Expo** - AI-Powered Clinical Decision Support for Radiologists

## Overview

This system integrates Natural Language Processing, rule-based scoring, and AI justification to help radiologists make informed decisions about CT scan requests. The current frontend is a modern clinical dashboard with a polished, presentation-ready interface.

## Demo Quick Start

1. Start the backend: `python api.py`
2. Start the frontend: `cd frontend` then `npm start`
3. Open `http://localhost:3000`
4. Try a sample input and click `Analyze Request`
5. Review the score, verdict, extracted findings, and AI justification

## Architecture

- **Backend**: FastAPI with Python
- **Frontend**: React.js
- **AI Core**: 
  - NLP Pipeline (Transformers)
  - Scoring Engine (ACR-based rules)
  - LLM Layer (Groq API)

## Current Status

- Backend API runs on `http://localhost:8000`
- Frontend runs on `http://localhost:3000`
- React production build completes successfully
- Backend API endpoints and end-to-end flow were verified locally

## Quick Start

### Prerequisites

1. Python 3.8+
2. Node.js 14+
3. Groq API Key (set in `.env` file)

### Installation

1. **Backend Setup**:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your GROQ_API_KEY
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
cd ..
```

### Running the Application

1. **Start the Backend API**:
```bash
python api.py
```
API will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

2. **Start the Frontend** (in a new terminal):
```bash
cd frontend
npm start
```
Frontend will be available at: http://localhost:3000

3. **Optional: Verify the frontend build**:
```bash
cd frontend
npm run build
```

## Usage

### Web Interface
1. Open http://localhost:3000 in your browser
2. Enter clinical indication text or use sample inputs
3. Click "Analyze Request" to get vetting results
4. Review the comprehensive analysis report

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Vetting analysis
curl -X POST http://localhost:8000/vet \
  -H "Content-Type: application/json" \
  -d '{"clinical_text": "35 year old male with abdominal pain..."}'
```

## Sample Test Cases

The system includes pre-built sample inputs:

1. **Acute Trauma** - High priority (APPROVE)
2. **Vague Pain** - Low priority (SOFT REJECT)  
3. **Acute Abdomen** - High priority (APPROVE)
4. **Urological** - Medium priority (FLAG FOR REVIEW)

## Features

### Clinical Analysis
- **Entity Extraction**: Age, sex, symptoms, duration
- **Red Flag Detection**: Peritoneal signs, instability, trauma
- **Clinical Categorization**: 9 predefined categories
- **Prior Imaging Detection**: Identifies previous studies

### Scoring System
- **Base Scores**: Category-specific (3-7 points)
- **Modifiers**: Red flags, urgency, prior imaging, duration
- **Thresholds**: Approve (7+), Flag (4-6), Reject (<4)
- **Final Verdict**: APPROVE, FLAG FOR REVIEW, SOFT REJECT

### AI Justification
- **Evidence-based Reasoning**: 2-3 sentence explanations
- **Alternative Suggestions**: When appropriate
- **Red Flags to Watch**: Clinical warning signs
- **Structured JSON Output**: Consistent format

## Project Structure

```
ct-vetting-system/
|
+--- api.py                 # FastAPI backend
+--- vetting_engine.py      # Main integration module
+--- e2e_test.py           # End-to-end verification script
|
+--- core/                  # AI processing modules
|   +--- nlp_pipeline.py    # NLP and entity extraction
|   +--- scoring_engine.py  # Rule-based scoring
|   +--- llm_layer.py       # AI justification
|
+--- frontend/              # React.js web interface
|   +--- src/
|   |   +--- App.js         # Main application
|   |   +--- App.css        # Styling
|   +--- public/
|   +--- package.json
|
+--- requirements.txt        # Python dependencies
+--- .env                   # Environment variables
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /vet` - Complete vetting analysis
- `GET /info` - API information

## Response Format

```json
{
  "success": true,
  "data": {
    "input": {"clinical_text": "..."},
    "nlp_processing": {"extracted_entities": {...}},
    "scoring": {"score_analysis": {...}},
    "justification": {"llm_output": {...}},
    "final_decision": {
      "verdict": "APPROVE",
      "score": 8.5,
      "category": "acute abdomen",
      "requires_review": false,
      "alternative_imaging": null
    }
  }
}
```

## Tech Stack

- **Backend**: FastAPI, Uvicorn, Pydantic
- **Frontend**: React, Axios, CSS Grid/Flexbox, responsive dashboard layout
- **AI/ML**: Transformers, Groq, Custom NLP
- **Development**: Hot reload, CORS enabled

## Future Enhancements

- Database integration for request history
- User authentication and profiles
- DICOM image analysis
- Learning system from outcomes
- Mobile app development
- Hospital EMR integration

## College Tech Expo Notes

This MVP demonstrates:
- **AI Integration**: Multiple AI models working together
- **Clinical Application**: Real-world medical decision support
- **Full Stack Development**: Backend API + Frontend UI
- **Modern Technologies**: FastAPI, React, Transformers
- **User Experience**: Clean, intuitive dashboard with a refined visual design

## Troubleshooting

**Common Issues:**
- **API Connection Error**: Ensure backend is running on localhost:8000
- **Model Loading**: First run downloads models (2-3 minutes)
- **Groq API Error**: Check GROQ_API_KEY in .env file
- **CORS Issues**: Backend includes CORS middleware for MVP

**Verified Local Test Flow:**
- Start backend with `python api.py`
- Start frontend with `cd frontend && npm start`
- Confirm frontend production build with `cd frontend && npm run build`
- Exercise the API with `GET /health` and `POST /vet`

**Performance Tips:**
- Models are cached after first load
- Use sample inputs for quick testing
- API responses include processing metadata

---

**Developed for College Tech Expo 2026**  
*AI-Powered Medical Decision Support System*
