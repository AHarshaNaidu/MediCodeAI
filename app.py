import streamlit as st
from groq import Groq

# Setup API key
api_key = st.secrets["api_key"]
client = Groq(api_key=api_key)

# Prompt Template
medical_coding_prompt = """
You are a medical coding assistant.
Given a clinical note, respond ONLY with appropriate ICD-10 and CPT codes in this format:

- Code: <code>
- Description: <short description>

DO NOT include thoughts, reasoning, or internal thinking.
NO explanations, NO <think> tags.
Only return the final codes.
"""


def truncate_content(content, max_chars=2000):
    return content[:max_chars] if content else ""

def call_medical_coder(note):
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": truncate_content(medical_coding_prompt, 500)},
            {"role": "user", "content": truncate_content(note)}
        ],
        "max_tokens": 1000
    }

    try:
        response = client.chat.completions.create(**data)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="MediCodeAI - AI Powered Medical Coding", page_icon="⚕️")
st.title("MediCodeAI")
st.caption("AI-Powered Medical Coding")

note = st.text_area("Enter Clinical Note:", placeholder="e.g. Patient presents with chronic shortness of breath...")

if st.button("Get Medical Codes"):
    if not note.strip():
        st.warning("Please enter a clinical note.")
    else:
        with st.spinner("Analyzing with MediCodeAI..."):
            result = call_medical_coder(note)
            if result:
                st.markdown("### Suggested Medical Codes:")
                st.code(result)
