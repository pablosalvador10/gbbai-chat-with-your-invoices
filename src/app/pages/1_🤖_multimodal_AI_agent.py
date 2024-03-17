import base64
import streamlit as st
from dotenv import load_dotenv
import time
import black
import os
from src.ocr.transformer import GPT4VisionManager
from utils.ml_logging import get_logger
from src.utilsfunc import save_uploaded_file

# Load environment variables from .env file
load_dotenv()

# Set up logger
logger = get_logger()

DELAY_TIME = 0.01
code = """"""

# System and user messages for processing
SYS_MESSAGE = """You are a seasoned software engineer focusing on TALEND ETL processes and migrations to Azure Data Factory (ADF). 
You excel at processing and summarizing complex UML, flow diagrams, and code, facilitating smooth migrations to Azure's ADF Data Factory,
offering expert guidance and precise assistance."""

USER_PROMPT = f"""
Please analyze the image (if provided) and/or the code. Follow this thought process carefully and take your time,
 as the migration of processes from TALEND ETL to Azure ADF needs to match perfectly:

1. **Summary**: Provide a brief overview of the TALEND ETL job, as depicted in the provided image or code. Highlight key points and the overarching theme, 
and describe the end-to-end especially as it pertains to the migration process to Azure Data Factory (ADF).

2. **Detailed Analysis**:
    - **Code Analysis**: If code is provided, detail its functionality and how it aligns with current ETL processes. 

    {code}

    If no code is provided, analyze the image and describe the workflow and its relevance to the migration effort.

    - **Diagram Analysis**: For any diagrams or UML designs, describe their structure and relevance to the migration effort, 
    ensuring a comprehensive understanding of the workflow and how it may be translated into ADF. Please understand each stage in detail and how it can be translated to ADF. 

3. **Translation of Key Functions**: Based on the analysis, provide a detailed, step-by-step translation of key functions from the TALEND ETL job to ADF. Each step should include:
    - The equivalent function in ADF.
    - A detailed explanation of how to implement the function in ADF.
    - Any specific tasks and resources needed for each step.

4. **Resources to Visit**: Provide a list of resources that may be helpful in the migration process. This could include documentation, tutorials, or other materials that will aid in the transition.

5. **Note**: If you are not 100% sure about the answer, please provide what you are sure about and ask more questions or add more detail. Do not answer if you are not 100% sure.

Take your time and provide a detailed analysis. This is a critical migration process and accuracy is paramount.

# Summary
<summary text>

# Detailed Analysis
## Code Analysis
<code analysis text>
## Diagram Analysis
<diagram analysis text>

# Translation of Key Functions
<step 1>
<step 2>
...
<step n>

# Python Code for Migrated Task
<Python code>

# Resources to Visit
[<resource 1>, <resource 2>, <resource 3>, ...]
"""

# Initialize GPT4VisionManager in session state
if "gpt4_vision_manager" not in st.session_state:
    st.session_state.gpt4_vision_manager = GPT4VisionManager()

# Function to convert image to base64 for embedding
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
# Chatbot interface
st.title("💬 Code Assistant - Interact with your code")

"""
🚀 Powered by Azure OpenAI. This Code Assistant helps you understand complex relationships in your code, generate new code, and migrate between 
different programming languages. 

In this example, we're using `GPT4 Turbo with vision` to demonstrate the multimodality capabilities of the Code Assistant in an interactive Streamlit app.

Explore more examples of the multimodal Code Assistant at [github.com/langchain-ai/streamlit-agent](https://github.com/langchain-ai/streamlit-agent).
"""

# About App expander
with st.expander("About this App"):
    st.markdown(
        """
        ### 🌟 Application Overview
        This application demonstrates the power of Azure AI in a real-time conversational context. It seamlessly integrates various Azure AI services to provide a sophisticated code analysis, generation, and migration experience.

        #### Key Features:
        - **Code Analysis**: Utilizes Azure AI to understand complex relationships in your code.
        - **Code Generation**: Employs Azure OpenAI GPT-4 for advanced code generation based on your requirements.
        - **Code Migration**: Leverages Azure AI to help you migrate your code between different programming languages.

        ### 🔧 Prerequisites and Dependencies
        To fully experience this application, the following Azure services are required:
        - Azure OpenAI Service: Set up an instance and obtain an API key for access to GPT-4 capabilities.
        - Azure AI Service: Necessary for analyzing, generating, and migrating code. A subscription key and region information are needed.
        """,
        unsafe_allow_html=True,
    )

# Function to save uploaded file and return path (synchronously for now)
def save_uploaded_file(uploaded_file):
    os.makedirs('tempDir', exist_ok=True)  # Ensure the directory exists
    file_path = os.path.join("tempDir", uploaded_file.name)
    with open(file_path, "wb") as f:
        contents = uploaded_file.read()
        f.write(contents)
    return file_path

def process_code(text: str) -> str:
    try:
        # Format the code using the 'black' formatter
        formatted_code = black.format_str(text, mode=black.FileMode())
        return formatted_code
    except black.InvalidInput as e:
        return f"Invalid input: {e}"

def process_input(image_paths, code):
    # User prompt with inserted code
    if code: # If code is provided
        user_prompt_with_code = USER_PROMPT.format(code=code)
    else:
        user_prompt_with_code = USER_PROMPT.format(code="No code provided.")

    logger.info(user_prompt_with_code)
    
    # Call GPT4 Vision Manager
    response = st.session_state.gpt4_vision_manager.call_gpt4v_image(
        image_paths,
        system_instruction=SYS_MESSAGE,
        user_instruction=user_prompt_with_code,
        ocr=True,
        use_vision_api=True,
        display_image=False,
        max_tokens=2000,
        seed=42,
    )
    return response

# Create two columns
col1, col2 = st.columns(2)

# Upload image or PDF file in the first column
uploaded_files = col1.file_uploader("Upload an image or PDF file", accept_multiple_files=True, type=["png", "jpg", "jpeg", "pdf"])

# Text area for user to paste code in the second column
code = col2.text_area("Paste your code here:")

# Main function to handle operations
def main(code):
    image_paths = []

    # Save uploaded files
    if uploaded_files:
        image_paths = [save_uploaded_file(uploaded_file) for uploaded_file in uploaded_files]

    # Process input if prompt is provided
    if image_paths or code:
        response = process_input(image_paths, code)
        st.write("### Answer")
        st.write(response)

if col2.button('Process information'):
    # Call your function here, passing the `code` variable
    result = process_code(code)
    main(code)

# Chat input for user to submit queries
if prompt := st.chat_input("Please translate this code to a better format? (e.g., Python to Java)"):
    # Trigger operations
    pass