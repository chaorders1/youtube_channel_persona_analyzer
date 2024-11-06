from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, Optional
import uvicorn
import sys
from pathlib import Path
import logging
from datetime import datetime
import json
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root directory to Python path
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

# Import the PersonaPipeline
from utility.persona_pipeline import PersonaPipeline

app = FastAPI(
    title="YouTube Channel Persona Analysis API",
    description="API for analyzing YouTube channel personas and content strategy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

class ChannelAnalysisRequest(BaseModel):
    """Request model for YouTube channel analysis."""
    youtube_channel_url: HttpUrl = Field(
        ...,
        description="Full YouTube channel URL",
        example="https://www.youtube.com/@AIJasonZ"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "youtube_channel_url": "https://www.youtube.com/@AIJasonZ"
            }
        }

class AnalysisResponse(BaseModel):
    """Response model for channel analysis results."""
    youtube_channel_url: str
    analysis_timestamp: str
    persona_analysis: Dict[str, Any]
    metrics: Dict[str, Any]
    recommendations: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "youtube_channel_url": "https://www.youtube.com/@AIJasonZ",
                "analysis_timestamp": "2024-11-06T12:00:00Z",
                "persona_analysis": {
                    "content_style": "Educational tech content",
                    "target_audience": "Tech enthusiasts and AI learners"
                },
                "metrics": {
                    "avg_views": 10000,
                    "engagement_rate": 8.5
                },
                "recommendations": {
                    "content_strategy": [
                        "Focus more on trending AI topics",
                        "Increase upload frequency"
                    ]
                }
            }
        }

def parse_analysis_file(file_path: Path) -> Dict[str, Any]:
    """
    Parse the analysis file content into structured data.
    
    Args:
        file_path: Path to the analysis file
        
    Returns:
        Dict containing parsed analysis data
    """
    try:
        content = file_path.read_text()
        # Add your parsing logic here to convert the markdown content
        # into structured data for the response
        return {
            "analysis": content,
            "summary": content[:500]  # Example: first 500 chars as summary
        }
    except Exception as e:
        logger.error(f"Error parsing analysis file: {e}")
        raise ValueError(f"Failed to parse analysis file: {str(e)}")

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_channel(request: ChannelAnalysisRequest) -> AnalysisResponse:
    """
    Analyze a YouTube channel and return persona insights.
    
    Args:
        request: ChannelAnalysisRequest object containing analysis parameters
        
    Returns:
        AnalysisResponse object containing detailed analysis results
        
    Raises:
        HTTPException: If channel analysis fails or invalid input
    """
    try:
        logger.info(f"Starting analysis for channel: {request.youtube_channel_url}")
        
        # Initialize and run the pipeline
        pipeline = PersonaPipeline(single_url=str(request.youtube_channel_url))
        pipeline.run_pipeline()
        
        # Get the latest analysis file
        data_dir = Path('data')
        if not data_dir.exists():
            raise FileNotFoundError("Data directory not found")
            
        analysis_files = list(data_dir.glob('crop_*_analysis.md'))
        if not analysis_files:
            raise FileNotFoundError("No analysis file generated")
            
        latest_analysis = max(analysis_files, key=lambda x: x.stat().st_mtime)
        analysis_data = parse_analysis_file(latest_analysis)
        
        return AnalysisResponse(
            youtube_channel_url=str(request.youtube_channel_url),
            analysis_timestamp=datetime.utcnow().isoformat() + "Z",
            persona_analysis=analysis_data,
            metrics={
                "analyzed_videos": 10,
                "comments_included": False
            },
            recommendations={
                "content_strategy": [],  # Add your recommendation logic here
                "engagement_suggestions": []
            }
        )
    except FileNotFoundError as e:
        logger.error(f"File not found error: {e}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during channel analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing channel: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status."""
    try:
        # Check if data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data_directory": str(data_dir.absolute()),
            "api_version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint to verify API is working."""
    return {
        "status": "online",
        "message": "YouTube Channel Persona Analysis API",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.post("/test-analyze")
async def test_analyze(request: ChannelAnalysisRequest):
    """Enhanced test endpoint with simulated pipeline stages."""
    try:
        stages = [
            ("Initializing Analysis", 10),
            ("Capturing Channel Screenshots", 30),
            ("Processing Images", 50),
            ("Analyzing Channel Content", 70),
            ("Generating Persona Report", 90),
            ("Finalizing Results", 100)
        ]
        
        # Simulate pipeline stages with actual data
        analysis_data = {
            "channel_info": {
                "name": "Sample Channel",
                "subscribers": "100K+",
                "total_videos": "500+",
                "join_date": "2020"
            },
            "content_analysis": {
                "main_topics": ["Technology", "AI", "Programming"],
                "video_style": "Educational/Tutorial",
                "avg_duration": "15-20 minutes"
            },
            "audience_insights": {
                "primary_demographic": "Tech professionals & students",
                "engagement_rate": "8.5%",
                "peak_activity": "Weekdays evenings"
            },
            "recommendations": [
                "Increase upload frequency",
                "Expand topic coverage",
                "Enhance community engagement"
            ]
        }

        # Return formatted analysis results
        return {
            "youtube_channel_url": str(request.youtube_channel_url),
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
            "persona_analysis": analysis_data,
            "metrics": {
                "analyzed_videos": 10,
                "engagement_metrics": {
                    "avg_likes": "5K+",
                    "avg_comments": "500+",
                    "view_retention": "65%"
                }
            },
            "recommendations": {
                "content_strategy": [
                    "Focus on trending tech topics",
                    "Create series-based content",
                    "Optimize video lengths"
                ],
                "engagement_suggestions": [
                    "Increase community posts",
                    "Host live Q&A sessions",
                    "Collaborate with similar channels"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error in test analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    try:
        # Change the uvicorn.run configuration
        uvicorn.run(
            "persona_api:app",  # Change from app to "persona_api:app"
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info",
            reload_dirs=[str(root_dir)]  # Add reload directory
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)