import os
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from PyPDF2 import PdfReader
import uvicorn

# Configure Google Generative AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Global knowledge base to store uploaded documents and HTML
KNOWLEDGE_BASE = {
    "docs": "",
    "html": ""
}

# Initialize FastAPI app
app = FastAPI(
    title="QA Agent Backend",
    description="AI-powered QA test case and script generation system",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Pydantic models for request/response
class TestCaseGenerateRequest(BaseModel):
    """Request model for generating test cases (optional parameters)"""
    pass


class TestCase(BaseModel):
    """Model for a single test case"""
    id: int
    description: str
    steps: List[str]
    expected_result: str


class ScriptGenerateRequest(BaseModel):
    """Request model for generating Selenium script"""
    test_case: dict
    html_content: Optional[str] = None


# Helper function to extract text from PDF
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file using PyPDF2"""
    try:
        from io import BytesIO
        pdf_reader = PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting PDF: {str(e)}")


# Helper function to extract text from TXT file
def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file"""
    try:
        return file_content.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading TXT file: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "QA Agent Backend API is running",
        "version": "1.0.0",
        "status": "operational",
        "knowledge_base_status": {
            "docs_loaded": len(KNOWLEDGE_BASE["docs"]) > 0,
            "html_loaded": len(KNOWLEDGE_BASE["html"]) > 0
        }
    }


@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(..., description="List of PDF or TXT files containing requirements/documentation"),
    html_file: UploadFile = File(..., description="HTML file of the application to be tested")
):
    """
    Upload documentation files and HTML file to build knowledge base.

    - **files**: List of PDF or TXT files containing business requirements, API specs, etc.
    - **html_file**: HTML file of the application interface to be tested

    Returns status confirming knowledge base has been built.
    """
    try:
        # Reset knowledge base
        KNOWLEDGE_BASE["docs"] = ""
        KNOWLEDGE_BASE["html"] = ""

        # Process documentation files (PDFs and TXTs)
        docs_text = []
        for file in files:
            file_content = await file.read()

            if file.filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_content)
                docs_text.append(f"--- Document: {file.filename} ---\n{text}\n")
            elif file.filename.lower().endswith('.txt'):
                text = extract_text_from_txt(file_content)
                docs_text.append(f"--- Document: {file.filename} ---\n{text}\n")
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Only PDF and TXT files are supported."
                )

        # Combine all documentation
        KNOWLEDGE_BASE["docs"] = "\n".join(docs_text)

        # Process HTML file
        html_content = await html_file.read()
        KNOWLEDGE_BASE["html"] = extract_text_from_txt(html_content)

        return {
            "status": "Knowledge Base Built",
            "details": {
                "documents_processed": len(files),
                "document_names": [f.filename for f in files],
                "html_file": html_file.filename,
                "total_doc_chars": len(KNOWLEDGE_BASE["docs"]),
                "total_html_chars": len(KNOWLEDGE_BASE["html"])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


@app.post("/generate-test-cases")
async def generate_test_cases():
    """
    Generate test cases based on uploaded documentation and HTML.

    Uses AI to analyze the requirements and HTML structure to generate 5 comprehensive test cases.

    Returns a list of test cases in JSON format.
    """
    try:
        # Check if knowledge base is populated
        if not KNOWLEDGE_BASE["docs"] or not KNOWLEDGE_BASE["html"]:
            raise HTTPException(
                status_code=400,
                detail="Knowledge base is empty. Please upload files first using /upload endpoint."
            )

        # Construct prompt for AI
        prompt = f"""You are a QA Lead with expertise in software testing and quality assurance.

Based strictly on the provided documentation and HTML structure below, generate exactly 5 comprehensive test cases.

DOCUMENTATION:
{KNOWLEDGE_BASE["docs"]}

HTML STRUCTURE:
{KNOWLEDGE_BASE["html"]}

REQUIREMENTS:
1. Analyze the business rules and requirements from the documentation
2. Examine the HTML structure to understand the UI elements and their IDs
3. Generate 5 test cases that cover critical functionality
4. Each test case must include: id (number), description (string), steps (array of strings), expected_result (string)
5. Focus on validation rules, user inputs, and business logic
6. Return ONLY valid JSON format

OUTPUT FORMAT (return only the JSON array, no markdown or additional text):
[
  {{
    "id": 1,
    "description": "Test case description",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "expected_result": "Expected outcome"
  }}
]

Generate the test cases now:"""

        # Call Gemini API
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        # Parse JSON response
        try:
            test_cases = json.loads(response_text)
            return {
                "status": "success",
                "test_cases": test_cases,
                "count": len(test_cases)
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw response for debugging
            return {
                "status": "success",
                "test_cases": response_text,
                "note": "Response was not valid JSON, returning raw text"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test cases: {str(e)}")


@app.post("/generate-script")
async def generate_script(request: ScriptGenerateRequest):
    """
    Generate a Selenium Python script for a given test case.

    - **test_case**: The test case object containing id, description, steps, and expected_result
    - **html_content**: Optional HTML content (if not provided, uses stored HTML from knowledge base)

    Returns Python Selenium script code.
    """
    try:
        # Use provided HTML or fall back to knowledge base
        html_content = request.html_content if request.html_content else KNOWLEDGE_BASE["html"]

        if not html_content:
            raise HTTPException(
                status_code=400,
                detail="No HTML content available. Either provide html_content in request or upload files first."
            )

        # Construct prompt for AI
        prompt = f"""You are a Senior QA Automation Engineer specializing in Selenium WebDriver with Python.

Generate a complete, production-ready Python Selenium script for the following test case.

TEST CASE:
{json.dumps(request.test_case, indent=2)}

HTML STRUCTURE (use the IDs and elements from this HTML):
{html_content}

REQUIREMENTS:
1. Use Python with Selenium WebDriver
2. Use the exact IDs and classes from the provided HTML
3. Include proper waits (WebDriverWait, expected_conditions)
4. Include error handling and assertions
5. Add comments explaining each step
6. Use Chrome WebDriver
7. Include setup and teardown
8. Make the script executable and complete
9. Return ONLY the Python code, no markdown formatting, no explanations

Generate the Selenium script now:"""

        # Call Gemini API
        response = model.generate_content(prompt)
        script_code = response.text.strip()

        # Clean up markdown code blocks if present
        if "```python" in script_code:
            script_code = script_code.split("```python")[1].split("```")[0].strip()
        elif "```" in script_code:
            script_code = script_code.split("```")[1].split("```")[0].strip()

        return {
            "status": "success",
            "script": script_code,
            "test_case_id": request.test_case.get("id", "unknown"),
            "language": "python",
            "framework": "selenium"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")


@app.get("/knowledge-base/status")
async def get_knowledge_base_status():
    """Get the current status of the knowledge base"""
    return {
        "docs_loaded": len(KNOWLEDGE_BASE["docs"]) > 0,
        "html_loaded": len(KNOWLEDGE_BASE["html"]) > 0,
        "docs_size": len(KNOWLEDGE_BASE["docs"]),
        "html_size": len(KNOWLEDGE_BASE["html"]),
        "docs_preview": KNOWLEDGE_BASE["docs"][:200] + "..." if KNOWLEDGE_BASE["docs"] else "",
        "html_preview": KNOWLEDGE_BASE["html"][:200] + "..." if KNOWLEDGE_BASE["html"] else ""
    }


@app.delete("/knowledge-base/clear")
async def clear_knowledge_base():
    """Clear the knowledge base"""
    KNOWLEDGE_BASE["docs"] = ""
    KNOWLEDGE_BASE["html"] = ""
    return {
        "status": "Knowledge base cleared",
        "docs_loaded": False,
        "html_loaded": False
    }


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
