import streamlit as st
from groq import Groq

# Setup API key
api_key = st.secrets["api_key"]
client = Groq(api_key=api_key)

# Prompt templates
PROMPTS = {
    "ICD-10": """
You are a medical coding assistant.
Given a clinical note, return only ICD-10 codes in this format:

- Code: <code>
- Description: <short description>

Do NOT include thoughts, reasoning, or explanations.
""",
    "CPT": """
You are a medical coding assistant.
Given a clinical note, return only CPT codes in this format:

- Code: <code>
- Description: <short description>

No internal thoughts or explanations.
"""
}

def truncate_content(content, max_chars=2000):
    return content[:max_chars] if content else ""

def call_medical_coder(note, prompt):
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": truncate_content(prompt, 500)},
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
st.title("⚕️ MediCodeAI")
st.caption("AI-Powered Medical Coding")

# Dropdown to select code type
code_type = st.selectbox("Select Code Type", ["ICD-10", "CPT"])

# Text input
note = st.text_area("Enter Clinical Note:", placeholder="e.g. Patient presents with chronic shortness of breath...")

# Button
if st.button("Get Medical Codes"):
    if not note.strip():
        st.warning("Please enter a clinical note.")
    else:
        with st.spinner("Analyzing with MediCodeAI..."):
            prompt = PROMPTS[code_type]
            result = call_medical_coder(note, prompt)
            if result:
                st.markdown("### Suggested Medical Codes:")
                st.code(result)

                # Additional functionality: generate enriched clinical statement
                st.markdown("---")
                st.markdown("### Enriched Clinical Statement (Based on Codes):")

                enhanced_prompt = f"""
You are a medical AI assistant.
Given the following clinical note and the {code_type} codes with descriptions, generate a human-readable enriched clinical statement that reflects the conditions and treatments described in the codes.
Do NOT include or mention the code numbers, just the medical context.

Clinical Note:
{note}

Codes:
{result}

Output:
"""
                enriched_result = call_medical_coder(note, enhanced_prompt)
                if enriched_result:
                    st.markdown(enriched_result)
