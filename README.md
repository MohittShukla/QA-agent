# Autonomous QA Agent

**Context-aware test case generation and Selenium automation powered by Google Gemini 2.5 Flash**

Transform your requirements documents and HTML files into production-ready test cases and automation scripts—instantly. No manual test writing required.

---

## 📊 Demo & Repository

- **Demo Video**: [Watch Demo](demo-video-link-placeholder)
- **Repository**: [GitHub Repository](repository-url-placeholder)

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│  PDF/TXT Docs   │
│  HTML File      │
└────────┬────────┘
         │ Upload
         ▼
┌─────────────────────────┐
│  FastAPI Backend        │
│  • File Ingestion       │
│  • Text Extraction      │
│  • Context Building     │
└────────┬────────────────┘
         │ Knowledge Base
         ▼
┌─────────────────────────┐
│  Gemini 2.5 Flash       │
│  • Prompt Engineering   │
│  • Structured Output    │
│  • Context Window       │
└────────┬────────────────┘
         │ AI Response
         ▼
┌─────────────────────────┐
│  Streamlit Frontend     │
│  • Test Case Display    │
│  • Script Generation    │
│  • Export & Download    │
└─────────────────────────┘
```

**Flow**: File Ingestion → Context Aggregation → AI Inference → Structured Test Generation → Selenium Script Creation

The system builds an in-memory knowledge base from uploaded documentation, constructs context-aware prompts, and leverages Gemini 2.5 Flash for high-speed inference with structured JSON output and Python code generation.

---

## ✨ Key Features

### Context-Aware Test Generation
Analyzes business requirements, API specifications, and HTML structure together to generate test cases that reflect actual validation rules and UI constraints.

### Hallucination Guardrails
- Strict prompt engineering instructs the model to generate tests "based strictly on provided documentation"
- HTML element IDs and classes are extracted and enforced in generated Selenium scripts
- JSON schema validation ensures structured, parsable output

### Selenium Code Generation
Produces production-ready Python Selenium scripts with:
- Exact element locators from uploaded HTML
- WebDriverWait and explicit waits
- Error handling and assertions
- Setup and teardown methods
- Inline documentation

### In-Memory Knowledge Base
Files are processed and stored in a global in-memory dictionary (`KNOWLEDGE_BASE`) for fast retrieval. No database required for this implementation.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | `FastAPI 0.115.5` |
| **AI Model** | `Google Gemini 2.5 Flash` |
| **Frontend** | `Streamlit 1.40.1` |
| **PDF Processing** | `PyPDF2 3.0.1` |
| **Server** | `Uvicorn 0.32.1` |
| **Environment** | `Python-dotenv 1.0.1` |

---

## 📋 Prerequisites

- **Python**: 3.9 or higher
- **Google Gemini API Key**: [Get your API key](https://makersuite.google.com/app/apikey)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd qa-agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Open `backend/.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Launch the Backend
```bash
cd backend
python main.py
```
Backend starts at `http://127.0.0.1:8000`

### 6. Launch the Frontend (New Terminal)
```bash
cd frontend
streamlit run app.py
```
Frontend opens at `http://localhost:8501`

**Ready to use in 30 seconds.**

---

## 📖 Usage Workflow

### Step 1: Upload Documents
In the **Streamlit sidebar**:
- Upload requirement documents (PDF or TXT) containing business rules, validation logic, or API specs
- Upload the HTML file of the application under test
- Click **"Upload & Analyze"**

The backend extracts text from PDFs using PyPDF2, reads TXT files, and builds the knowledge base.

### Step 2: Generate Test Cases
- Click **"Generate Test Cases"** in the main interface
- The system constructs a prompt containing all documentation and HTML structure
- Gemini 2.5 Flash returns 5 test cases in JSON format with:
  - Test case ID
  - Description
  - Step-by-step instructions
  - Expected result

### Step 3: Create Selenium Scripts
- Expand any test case
- Click **"Generate Selenium Script"**
- The AI generates a Python Selenium script using actual element IDs from the uploaded HTML
- Download the script as a `.py` file

---

## 🔌 API Reference

### `POST /upload`
**Description**: Upload documentation files and HTML to build the knowledge base.

**Request**:
- `files`: List of PDF or TXT files (multipart/form-data)
- `html_file`: Single HTML file (multipart/form-data)

**Response**:
```json
{
  "status": "Knowledge Base Built",
  "details": {
    "documents_processed": 2,
    "document_names": ["requirements.txt", "api_spec.txt"],
    "html_file": "checkout.html",
    "total_doc_chars": 5420,
    "total_html_chars": 3210
  }
}
```

---

### `POST /generate-test-cases`
**Description**: Generate 5 test cases based on uploaded documentation and HTML.

**Request**: None (uses stored knowledge base)

**Response**:
```json
{
  "status": "success",
  "test_cases": [
    {
      "id": 1,
      "description": "Validate CVV field accepts only 3 digits",
      "steps": [
        "Navigate to checkout page",
        "Enter valid card details",
        "Enter '12' in CVV field",
        "Click Pay Now"
      ],
      "expected_result": "Error message: 'CVV must be exactly 3 digits'"
    }
  ],
  "count": 5
}
```

---

### `POST /generate-script`
**Description**: Generate a Selenium Python script for a specific test case.

**Request**:
```json
{
  "test_case": {
    "id": 1,
    "description": "Test description",
    "steps": ["Step 1", "Step 2"],
    "expected_result": "Expected outcome"
  },
  "html_content": "Optional HTML override"
}
```

**Response**:
```json
{
  "status": "success",
  "script": "from selenium import webdriver\n...",
  "test_case_id": 1,
  "language": "python",
  "framework": "selenium"
}
```

---

### `GET /knowledge-base/status`
**Description**: Check the current knowledge base status.

**Response**:
```json
{
  "docs_loaded": true,
  "html_loaded": true,
  "docs_size": 5420,
  "html_size": 3210,
  "docs_preview": "CHECKOUT PAYMENT SYSTEM...",
  "html_preview": "<!DOCTYPE html>..."
}
```

---

### `DELETE /knowledge-base/clear`
**Description**: Clear the in-memory knowledge base.

**Response**:
```json
{
  "status": "Knowledge base cleared",
  "docs_loaded": false,
  "html_loaded": false
}
```

---

## 📁 Project Structure

```
qa-agent/
├── backend/
│   ├── main.py                # FastAPI backend server
│   └── .env                   # Backend environment variables
├── frontend/
│   └── app.py                 # Streamlit frontend application
├── test_assets/
│   ├── checkout.html          # Sample HTML test asset
│   ├── requirements_doc.txt   # Sample business requirements
│   └── api_spec.txt           # Sample API specification
├── requirements.txt           # Python dependencies
├── .env                       # Root environment variables
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

---

## 🔍 How It Works

### Knowledge Base Construction
When files are uploaded via `/upload`:
1. PDFs are processed using `PyPDF2.PdfReader` to extract text page-by-page
2. TXT files are decoded as UTF-8
3. All documentation is concatenated into `KNOWLEDGE_BASE["docs"]`
4. HTML file is stored as-is in `KNOWLEDGE_BASE["html"]`

### Prompt Engineering
The system constructs a detailed prompt that includes:
- Role definition ("You are a QA Lead...")
- Full documentation text
- Complete HTML structure
- Output format specification (JSON schema)
- Instruction to generate exactly 5 test cases

### AI Inference
- Model: `gemini-2.5-flash` for high-speed generation
- Safety settings configured to `block_none` for all categories
- Response parsing handles both raw JSON and markdown-wrapped JSON
- Fallback mechanism returns raw text if JSON parsing fails

### Script Generation
For Selenium scripts:
- Test case details are passed as JSON
- HTML structure is included for element ID extraction
- Model is instructed to use exact IDs and classes
- Response is cleaned of markdown code blocks
- Ready-to-execute Python code is returned

---

## 🛡️ Error Handling

The system includes comprehensive error handling:
- **Empty Knowledge Base**: Returns 400 if files not uploaded
- **API Failures**: Logs Gemini API errors with full traceback
- **Safety Filters**: Detects and reports blocked responses
- **JSON Parsing**: Falls back to raw text if structured output fails
- **Connection Errors**: Frontend displays clear error messages

---

## 🧪 Sample Test Assets

Three test assets are included in the `test_assets/` directory:

### `test_assets/checkout.html`
A modern payment form with fields for:
- Name (`id="name-input"`)
- Email (`id="email-input"`)
- Credit Card (`id="cc-input"`)
- Expiry (`id="expiry-input"`)
- CVV (`id="cvv-input"`)
- Submit button (`id="submit-btn"`)

### `test_assets/requirements_doc.txt`
Business requirements including:
- User must be 18+
- CVV must be 3 digits
- Email must be valid format
- Credit card validation rules
- Security requirements

### `test_assets/api_spec.txt`
Payment API specification:
- `POST /api/pay` endpoint
- 200 response for success
- 400 response for validation errors
- Request/response schemas
- Error codes and messages

---

## 🐛 Troubleshooting

### "500 Server Error" when generating test cases
**Check**:
1. Verify your `.env` file contains a valid `GEMINI_API_KEY`
2. Review backend terminal logs for detailed error messages
3. Ensure uploaded documents are not empty
4. Check internet connectivity for Gemini API access

### "Cannot connect to backend server"
**Solution**: Ensure `python main.py` is running from the `backend/` directory on port 8000. Visit `http://127.0.0.1:8000` to confirm.

### "Knowledge base is empty"
**Solution**: Upload files via the sidebar first. Check `/knowledge-base/status` endpoint to verify.

---

## 📚 API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔐 Security Notes

- The `.env` file is git-ignored to prevent API key exposure
- CORS is configured to allow all origins (adjust for production)
- Knowledge base is in-memory only (resets on server restart)
- Uploaded files are never persisted to disk

---

## 🎯 Design Decisions

### Why In-Memory Storage?
This implementation uses a global dictionary for simplicity and speed. For production use cases requiring persistence, consider Redis or a database backend.

### Why Gemini 2.5 Flash?
Optimized for high-speed inference while maintaining quality. Ideal for structured output generation (JSON) and code synthesis tasks.

### Why Strict Prompting?
Explicit instructions ("based strictly on provided documentation") reduce hallucination and ensure generated test cases align with actual requirements.

---

## 📄 License

This project is provided as-is for educational and assignment purposes.

---

## 🤝 Contributing

This is an assignment project. Contributions are not currently accepted.

---

**Built with FastAPI, Streamlit, and Google Gemini 2.5 Flash**
