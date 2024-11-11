from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from markdown_it import MarkdownIt
import httpx
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize markdown converter with plugins and features
md = (
    MarkdownIt('commonmark', {
        'breaks': True,  # Convert '\n' in paragraphs into <br>
        'html': True,    # Enable HTML tags in source
        'linkify': True  # Autoconvert URL-like text to links
    })
    .enable('table')     # Enable table syntax
    .enable('strikethrough')
)

# Get the absolute path to the web_app directory
WEB_APP_DIR = Path(__file__).parent

app = FastAPI(title="YouTube Channel Persona Analysis Web App")

# Update the static files mounting with absolute path
app.mount("/static", StaticFiles(directory=str(WEB_APP_DIR / "static")), name="static")

# Initialize templates
templates = Jinja2Templates(directory="web_app/templates")

# API endpoint configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/analyze")
async def analyze_channel(request: Request, youtube_channel_url: str = Form(...)):
    """Handle channel analysis request and return results."""
    try:
        if not youtube_channel_url:
            raise HTTPException(status_code=400, detail="YouTube channel URL is required")

        logger.info(f"Making request to API: {API_BASE_URL}/test-analyze")
        
        # Make request to the analysis API with longer timeout
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{API_BASE_URL}/test-analyze",
                    json={"youtube_channel_url": youtube_channel_url},
                    timeout=300.0  # Increased timeout to 5 minutes
                )
                
                logger.info(f"API Response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_detail = f"API Error: {response.text}"
                    logger.error(error_detail)
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_detail
                    )
                    
                analysis_results = response.json()
                
                # Convert markdown to HTML using markdown-it-py
                html_content = md.render(analysis_results["analysis_content"])
                
                formatted_results = {
                    "youtube_channel_url": analysis_results["youtube_channel_url"],
                    "analysis_timestamp": analysis_results["analysis_timestamp"],
                    "analysis_content": html_content,  # Now contains HTML
                    "source_file": analysis_results["source_file"]
                }
                
                return templates.TemplateResponse(
                    "index.html",
                    {
                        "request": request,
                        "results": formatted_results,
                        "channel_url": youtube_channel_url,
                        "html_content": html_content  # Pass HTML content to template
                    }
                )
                
            except httpx.RequestError as e:
                logger.error(f"Request error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to API: {str(e)}"
                )
            
    except HTTPException as e:
        logger.error(f"HTTP Exception: {str(e)}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": e.detail
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"An unexpected error occurred: {str(e)}"
            }
        ) 