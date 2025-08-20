import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import os

# Adjust imports to be relative
from .main import analyze_page
from .test_generator import generate_basic_load_test
from .jmeter_exporter import export_to_jmx
from .loadrunner_exporter import export_to_loadrunner

app = FastAPI(
    title="AI-Powered Performance Test Case Generator API",
    description="An API to analyze a web application and generate performance test scripts.",
    version="1.0.0"
)

# Allow CORS for the React frontend, which will run on a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allowing all origins for simplicity in this environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str = Field(..., example="http://books.toscrape.com/")
    format: Literal['jmeter', 'loadrunner'] = Field(..., example="jmeter")

class AnalyzeResponse(BaseModel):
    message: str
    outputFile: str

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_and_generate(request: AnalyzeRequest):
    """
    Analyzes a given URL and generates a performance test script in the specified format.
    """
    try:
        print(f"Received request for URL: {request.url}, Format: {request.format}")

        # The root directory for output should be the main project root
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # Step 1: Analyze the page
        analysis_data = await analyze_page(request.url)
        if "error" in analysis_data:
            raise HTTPException(status_code=500, detail=f"Failed to analyze page: {analysis_data['error']}")

        # Step 2: Generate a test case
        test_case_data = generate_basic_load_test(analysis_data)
        if "No test case generated" in test_case_data.get("test_case_name", ""):
            raise HTTPException(status_code=404, detail="Could not generate a test case from the URL. No navigation links found.")

        # Step 3: Export to the chosen format
        output_path = ""
        if request.format == 'jmeter':
            output_path = export_to_jmx(test_case_data, filename="test_plan.jmx", output_dir=output_dir)
        elif request.format == 'loadrunner':
            output_path = export_to_loadrunner(test_case_data, script_name="GeneratedLRScript", output_dir=output_dir)

        print(f"Successfully generated script at: {output_path}")
        return {
            "message": f"{request.format.capitalize()} script generated successfully!",
            "outputFile": output_path
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

if __name__ == "__main__":
    # This allows running the server directly for development
    # Command: python -m ai_engine.api_server
    uvicorn.run(app, host="0.0.0.0", port=8000)
