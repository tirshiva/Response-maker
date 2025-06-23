import streamlit as st
import re
import json
from template_manager import list_templates, load_template, save_template

TEMPLATE_DIR = 'templates'

def parse_template_info(filename):
    # Expecting format: useralias_skill_templatename.json
    name = filename.rsplit('.', 1)[0]
    parts = name.split('_')
    if len(parts) >= 3:
        user = parts[0]
        skill = parts[1]
        template_shortname = '_'.join(parts[2:])
    elif len(parts) == 2:
        user = parts[0]
        skill = parts[1]
        template_shortname = ''
    else:
        user = 'Unknown'
        skill = 'Unknown'
        template_shortname = ''
    return user, skill, template_shortname

st.set_page_config(page_title="Response Maker", layout="centered")
st.title("📧 Response Maker")

tabs = st.tabs(["Generate Response", "Add New Template", "Edit Template"])

# --- Tab 1: Generate Response ---
with tabs[0]:
    template_files = list_templates()
    if not template_files:
        st.warning("No templates found. Please add a template first.")
    else:
        # Parse user, skill, and template name from filenames
        user_skill_template_list = [parse_template_info(f) for f in template_files]
        users = sorted(set(u for u, _, _ in user_skill_template_list))
        skills = sorted(set(s for _, s, _ in user_skill_template_list))
        selected_users = st.multiselect("Filter by User Alias", users, default=users)
        selected_skills = st.multiselect("Filter by Skill", skills, default=skills)
        filtered_indices = [i for i, (u, s, _) in enumerate(user_skill_template_list) if u in selected_users and s in selected_skills]
        if not filtered_indices:
            st.info("No templates match the selected filters.")
        else:
            filtered_files = [template_files[i] for i in filtered_indices]
            templates = [load_template(f) for f in filtered_files]
            template_labels = [f"{t['name']} ({t.get('description', 'No description')})" for t in templates]
            selected_idx = st.selectbox("Choose a template", range(len(filtered_files)), format_func=lambda i: template_labels[i])
            selected_template_file = filtered_files[selected_idx]
            template = templates[selected_idx]
            st.markdown(f"**Template:** {template['name']}")
            st.markdown(f"**Description:** {template.get('description', 'No description provided.')}")
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
                        const textarea = window.parent.document.querySelector('textarea[data-testid=\"stTextArea\"]');
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
    st.markdown("""
    <div style='background-color:rgba(220,220,220,0.7);padding:18px 16px 16px 16px;border-radius:8px;margin-bottom:18px;border:1.5px solid #888;'>
        <span style='font-size:1.1em;font-weight:bold;color:#222;'>Anyone can add a new template!</span><br><br>
        <b>Template Name:</b> <code>[useralias]_[skill]_[templatename]</code> <br>
        <b>Example:</b> <code>tirshiva_ILAC_reimbursement</code><br>
        <b>Parts:</b> <code>useralias</code> (your name), <code>skill</code> (department), <code>templatename</code> (purpose)<br>
        <b>Description:</b> Briefly state when to use this template.<br>
        <b>All templates are shared with all users.</b>
    </div>
    """, unsafe_allow_html=True)
    st.header("Add a New Email Template")
    template_name = st.text_input("Template Name (e.g., tirshiva_ILAC_reimbursement)")
    template_description = st.text_input("Short Description (when to use this template)")
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
        elif not template_description.strip():
            st.error("Short description is required.")
        else:
            variables = [v.strip() for v in custom_vars.split(',') if v.strip()]
            template_data = {
                "name": template_name.strip(),
                "body": email_body,
                "variables": variables,
                "description": template_description.strip()
            }
            filename = f"{template_name.strip().replace(' ', '_').lower()}.json"
            save_template(filename, template_data)
            st.success(f"Template '{template_name}' saved!")
            st.experimental_rerun()

# --- Tab 3: Edit Template ---
with tabs[2]:
    st.header("Edit an Existing Template")
    template_files = list_templates()
    if not template_files:
        st.warning("No templates found to edit.")
    else:
        selected_template_file = st.selectbox("Select a template to edit", template_files, key="edit_template_select")
        template = load_template(selected_template_file)
        if template is None:
            st.error("Could not load the selected template.")
        else:
            # Pre-fill fields
            new_name = st.text_input("Template Name (cannot be changed)", value=selected_template_file.rsplit('.', 1)[0], disabled=True)
            new_description = st.text_input("Short Description (when to use this template)", value=template.get("description", ""))
            new_body = st.text_area("Email body (use {variable} for placeholders)", value=template.get("body", ""), height=300)
            detected_vars = re.findall(r'\{(.*?)\}', new_body)
            detected_vars = list(dict.fromkeys([v.strip() for v in detected_vars if v.strip()]))
            st.info(f"Detected variables: {', '.join(detected_vars) if detected_vars else 'None'}")
            custom_vars = st.text_input("Edit variables (comma-separated)", value=", ".join(detected_vars))
            if st.button("Save Changes", key="edit_save_btn"):
                if not new_body.strip():
                    st.error("Email body is required.")
                elif not new_description.strip():
                    st.error("Short description is required.")
                else:
                    variables = [v.strip() for v in custom_vars.split(',') if v.strip()]
                    template_data = {
                        "name": template.get("name", new_name),
                        "body": new_body,
                        "variables": variables,
                        "description": new_description.strip()
                    }
                    save_template(selected_template_file, template_data)
                    st.success(f"Template '{selected_template_file}' updated!") 