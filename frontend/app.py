import streamlit as st
import requests
from typing import List, Dict
import json

# Page configuration
st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://127.0.0.1:8000"

# Session state initialization
if 'test_cases' not in st.session_state:
    st.session_state.test_cases = None
if 'upload_success' not in st.session_state:
    st.session_state.upload_success = False
if 'generated_scripts' not in st.session_state:
    st.session_state.generated_scripts = {}


# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .status-success {
        padding: 1rem;
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .status-error {
        padding: 1rem;
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .status-warning {
        padding: 1rem;
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .test-case-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #374151;
    }
    .stButton button {
        width: 100%;
        border-radius: 0.375rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .upload-section {
        background-color: #f9fafb;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
    }
    </style>
""", unsafe_allow_html=True)


def upload_files(doc_files: List, html_file) -> Dict:
    """Upload documentation and HTML files to the backend"""
    try:
        files = []

        # Add documentation files
        for doc_file in doc_files:
            files.append(('files', (doc_file.name, doc_file.getvalue(), doc_file.type)))

        # Add HTML file
        files.append(('html_file', (html_file.name, html_file.getvalue(), html_file.type)))

        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend server. Please ensure the FastAPI server is running on port 8000.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Upload failed: {str(e)}")
        return None


def generate_test_cases() -> Dict:
    """Generate test cases from uploaded documents"""
    try:
        response = requests.post(f"{API_BASE_URL}/generate-test-cases")
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Show detailed error message from backend
        try:
            error_detail = e.response.json().get('detail', str(e))
            st.error(f"Test case generation failed: {error_detail}")
        except:
            st.error(f"Test case generation failed: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Test case generation failed: {str(e)}")
        return None


def generate_script(test_case: Dict) -> Dict:
    """Generate Selenium script for a specific test case"""
    try:
        payload = {"test_case": test_case}
        response = requests.post(
            f"{API_BASE_URL}/generate-script",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Script generation failed: {str(e)}")
        return None


# Header
st.markdown('<div class="main-header">Autonomous QA Agent 🤖</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered test case generation and automation script creation</div>', unsafe_allow_html=True)

st.divider()

# Sidebar - Upload Section
with st.sidebar:
    st.header("Upload Documents")

    st.markdown("### Support Documents")
    st.caption("Upload requirement docs, API specs, or business rules (PDF/TXT)")
    doc_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'txt'],
        accept_multiple_files=True,
        key="doc_uploader",
        label_visibility="collapsed"
    )

    st.markdown("### Target HTML")
    st.caption("Upload the HTML file of the application to test")
    html_file = st.file_uploader(
        "Choose HTML file",
        type=['html'],
        accept_multiple_files=False,
        key="html_uploader",
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Upload button
    upload_button = st.button("📤 Upload & Analyze", type="primary", use_container_width=True)

    if upload_button:
        if not doc_files:
            st.warning("Please upload at least one support document.")
        elif not html_file:
            st.warning("Please upload an HTML file.")
        else:
            with st.spinner("Uploading files and building knowledge base..."):
                result = upload_files(doc_files, html_file)

                if result and result.get('status') == 'Knowledge Base Built':
                    st.session_state.upload_success = True
                    st.session_state.test_cases = None
                    st.session_state.generated_scripts = {}

                    st.success("✓ Files uploaded successfully")
                    with st.expander("Upload Details"):
                        st.json(result.get('details', {}))
                else:
                    st.session_state.upload_success = False

    # Status indicator
    if st.session_state.upload_success:
        st.markdown("""
            <div style='background-color: #d1fae5; padding: 0.75rem; border-radius: 0.375rem; margin-top: 1rem;'>
                <div style='color: #065f46; font-weight: 500;'>✓ Knowledge Base Ready</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Info section
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        **Step 1:** Upload your documents
        - Add requirement docs (PDF/TXT)
        - Add target HTML file
        - Click "Upload & Analyze"

        **Step 2:** Generate test cases
        - Click "Generate Test Cases"
        - Review generated test cases

        **Step 3:** Create automation scripts
        - Click "Generate Selenium Script" for any test case
        - Copy and use the generated code
        """)

# Main content area
if not st.session_state.upload_success:
    st.info("👈 Please upload documents using the sidebar to get started.")
else:
    # Generate Test Cases Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Generate Test Cases", type="primary", use_container_width=True):
            with st.spinner("Analyzing documents and generating test cases..."):
                result = generate_test_cases()

                if result and result.get('status') == 'success':
                    st.session_state.test_cases = result.get('test_cases', [])
                    st.session_state.generated_scripts = {}

    st.markdown("<br>", unsafe_allow_html=True)

    # Display test cases
    if st.session_state.test_cases:
        st.subheader("Generated Test Cases")
        st.caption(f"Total: {len(st.session_state.test_cases)} test cases")

        st.markdown("<br>", unsafe_allow_html=True)

        # Display each test case in an expander
        for idx, test_case in enumerate(st.session_state.test_cases):
            tc_id = test_case.get('id', idx + 1)
            description = test_case.get('description', 'No description')
            steps = test_case.get('steps', [])
            expected_result = test_case.get('expected_result', 'No expected result')

            with st.expander(f"**Test Case {tc_id}:** {description}", expanded=False):
                # Test case details
                st.markdown(f"**Description:**")
                st.info(description)

                st.markdown("**Test Steps:**")
                for step_idx, step in enumerate(steps, 1):
                    st.markdown(f"{step_idx}. {step}")

                st.markdown("**Expected Result:**")
                st.success(expected_result)

                st.markdown("---")

                # Generate script button
                script_key = f"script_{tc_id}"

                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    if st.button(
                        "⚡ Generate Selenium Script",
                        key=f"gen_btn_{tc_id}",
                        use_container_width=True
                    ):
                        with st.spinner("Generating automation script..."):
                            script_result = generate_script(test_case)

                            if script_result and script_result.get('status') == 'success':
                                st.session_state.generated_scripts[script_key] = script_result.get('script', '')

                # Display generated script
                if script_key in st.session_state.generated_scripts:
                    st.markdown("**Generated Selenium Script:**")
                    st.code(
                        st.session_state.generated_scripts[script_key],
                        language='python',
                        line_numbers=True
                    )

                    # Download button
                    st.download_button(
                        label="📥 Download Script",
                        data=st.session_state.generated_scripts[script_key],
                        file_name=f"test_case_{tc_id}_selenium.py",
                        mime="text/x-python",
                        key=f"download_{tc_id}"
                    )

    elif st.session_state.upload_success:
        st.info("Click 'Generate Test Cases' button above to create test cases from your uploaded documents.")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.caption("Powered by Google Gemini AI • Built with Streamlit and FastAPI")
