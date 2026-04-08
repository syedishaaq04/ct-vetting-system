#!/usr/bin/env python3
"""
FastAPI Backend for CT Scan Vetting System
MVP for College Tech Expo
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import sys
from pathlib import Path

# Add core directory to path
sys.path.append(str(Path(__file__).parent / "core"))

try:
    from vetting_engine import VettingEngine
except ImportError:
    print("Error: Could not import VettingEngine")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="CT Scan Vetting API",
    description="MVP API for CT scan vetting system",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP - allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vetting engine
vetting_engine = VettingEngine()

# Pydantic models for request/response
class VettingRequest(BaseModel):
    clinical_text: str
    
class VettingResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    error: str = None

class HealthResponse(BaseModel):
    status: str
    message: str
    engine_version: str

@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        engine_version=vetting_engine.version
    )

@app.post("/vet", response_model=VettingResponse)
async def vet_ct_scan(request: VettingRequest):
    """
    Main vetting endpoint
    
    Takes clinical text and returns complete vetting analysis
    """
    try:
        # Validate input
        if not request.clinical_text or len(request.clinical_text.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Clinical text must be at least 10 characters long"
            )
        
        # Process through vetting engine
        result = vetting_engine.vet_request(request.clinical_text)
        
        # Check for processing errors
        if "error" in result:
            return VettingResponse(
                success=False,
                error=result["error"]["message"]
            )
        
        return VettingResponse(
            success=True,
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return VettingResponse(
            success=False,
            error=f"Processing error: {str(e)}"
        )

@app.get("/info")
async def api_info():
    """API information and usage"""
    return {
        "name": "CT Scan Vetting API",
        "version": "1.0.0",
        "description": "MVP API for CT scan vetting system",
        "endpoints": {
            "GET /": "Health check",
            "GET /health": "Health check (alias)",
            "POST /vet": "Complete vetting analysis",
            "GET /info": "API information"
        },
        "usage_example": {
            "endpoint": "POST /vet",
            "request": {"clinical_text": "35 year old male with abdominal pain..."},
            "response": {"success": True, "data": {"final_decision": {}, "nlp_processing": {}, "scoring": {}, "justification": {}}}
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting CT Scan Vetting API...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
