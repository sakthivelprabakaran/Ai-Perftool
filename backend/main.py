from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright

# Import the core logic from the ai-engine package
# Note: This requires the ai-engine to be installed in the environment
from ai_engine.main import analyze_page
from ai_engine.test_generator import generate_basic_load_test
from ai_engine.jmeter_exporter import export_to_jmx

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    print("Starting up and launching browser...")
    p = await async_playwright().start()
    browser = await p.chromium.launch()
    app.state.browser = browser
    app.state.playwright = p
    yield
    # On shutdown
    print("Shutting down and closing browser...")
    await app.state.browser.close()
    await app.state.playwright.stop()


app = FastAPI(
    title="AI-Powered Performance Test Case Generator API",
    description="The backend server that runs the analysis engine and serves the frontend.",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS middleware to allow requests from the frontend
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173", # Default port for Vite React apps
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Performance Test Case Generator Backend"}

@app.post("/analyze")
async def run_analysis(request: Request, url_request: UrlRequest):
    """
    Receives a URL, runs the full pipeline (analysis, generation, export),
    and returns the final JMX file content as an XML response.
    """
    print(f"Received request to analyze URL: {url_request.url}")

    browser = request.app.state.browser

    # 1. Analyze the page using the shared browser instance
    analysis_data = await analyze_page(url_request.url, browser)

    if 'error' in analysis_data:
        return {"error": analysis_data['error']}

    # 2. Generate the test case structure
    test_case_data = generate_basic_load_test(analysis_data)

    # 3. Export to JMX format
    jmx_content = export_to_jmx(test_case_data)

    # 4. Return the JMX content as an XML response
    return Response(content=jmx_content, media_type="application/xml")
