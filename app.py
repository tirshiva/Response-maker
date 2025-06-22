import streamlit as st
import re
import os
import json
from template_manager import list_templates, load_template

TEMPLATE_DIR = 'templates'

st.set_page_config(page_title="Response Maker", layout="centered")
st.title("Response Maker")

tabs = st.tabs(["Generate Response", "Add New Template"])

# --- Tab 1: Generate Response ---
with tabs[0]:
    template_files = list_templates(TEMPLATE_DIR)
    if not template_files:
        st.warning("No templates found. Please add a template first.")
    else:
        selected_template_file = st.selectbox("Choose a template", template_files)
        template = load_template(selected_template_file, TEMPLATE_DIR)
        st.markdown(f"**Template:** {template['name']}")
        st.markdown("**Email Preview:**")
        st.code(template['body'], language='markdown')
        st.subheader("Fill in the variables:")
        user_inputs = {}
        for var in template['variables']:
            user_inputs[var] = st.text_input(f"{var.replace('_', ' ').capitalize()}")
        def fill_template(body, variables):
            return body.format(**variables)
        if st.button("Generate Response"):
            try:
                response = fill_template(template['body'], user_inputs)
                st.success("Generated Email:")
                st.text_area("Response", response, height=400, key="response_box")
                st.code(response, language='markdown')
                st.write('---')
                st.download_button("Download as .txt", response, file_name="response.txt")
                # Add JS to detect copy event and show a message
                st.markdown(
                    '''<script>
                    const textarea = window.parent.document.querySelector('textarea[data-testid="stTextArea"]');
                    if (textarea) {
                        textarea.addEventListener('copy', function() {
                            const streamlitDoc = window.parent.document;
                            let msg = streamlitDoc.getElementById('copy-msg');
                            if (!msg) {
                                msg = streamlitDoc.createElement('div');
                                msg.id = 'copy-msg';
                                msg.style.position = 'fixed';
                                msg.style.top = '10px';
                                msg.style.right = '10px';
                                msg.style.background = '#4BB543';
                                msg.style.color = 'white';
                                msg.style.padding = '10px 20px';
                                msg.style.borderRadius = '8px';
                                msg.style.zIndex = 9999;
                                msg.innerText = 'Email is copied';
                                streamlitDoc.body.appendChild(msg);
                                setTimeout(() => { msg.remove(); }, 2000);
                            }
                        });
                    }
                    </script>''',
                    unsafe_allow_html=True
                )
            except KeyError as e:
                st.error(f"Missing value for variable: {e}")

# --- Tab 2: Add New Template ---
with tabs[1]:
    st.header("Add a New Email Template")
    template_name = st.text_input("Template Name")
    email_body = st.text_area("Paste your email template here. Use {variable} for placeholders.", height=300)
    detected_vars = []
    if email_body:
        detected_vars = re.findall(r'\{(.*?)\}', email_body)
        detected_vars = list(dict.fromkeys([v.strip() for v in detected_vars if v.strip()]))  # unique, non-empty
        st.info(f"Detected variables: {', '.join(detected_vars) if detected_vars else 'None'}")
    custom_vars = st.text_input("Edit variables (comma-separated)", value=", ".join(detected_vars))
    if st.button("Save Template"):
        if not template_name.strip():
            st.error("Template name is required.")
        elif not email_body.strip():
            st.error("Email body is required.")
        else:
            variables = [v.strip() for v in custom_vars.split(',') if v.strip()]
            template_data = {
                "name": template_name.strip(),
                "body": email_body,
                "variables": variables
            }
            filename = f"{template_name.strip().replace(' ', '_').lower()}.json"
            filepath = os.path.join(TEMPLATE_DIR, filename)
            os.makedirs(TEMPLATE_DIR, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
            st.success(f"Template '{template_name}' saved!")
            st.experimental_rerun() 