import streamlit as st
import re
import json
from template_manager import list_templates, load_template, save_template, clear_template_cache

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

def show_retry_button(context_key):
    if st.button("Retry", key=f"retry_{context_key}"):
        st.rerun()

def update_recent_templates(template_file):
    if 'recent_templates' not in st.session_state:
        st.session_state['recent_templates'] = []
    if template_file in st.session_state['recent_templates']:
        st.session_state['recent_templates'].remove(template_file)
    st.session_state['recent_templates'].insert(0, template_file)
    st.session_state['recent_templates'] = st.session_state['recent_templates'][:3]

def show_template_stats(template_files):
    st.markdown(f"<div style='background-color:#f0f4fa;padding:8px 16px;border-radius:8px;display:inline-block;margin-bottom:10px;font-size:1.1em;'><b>📊 Total Email Templates:</b> {len(template_files)}</div>", unsafe_allow_html=True)

tabs = st.tabs(["Generate Response", "Add New Template", "Edit Template"])

# --- Tab 1: Generate Response ---
with tabs[0]:
    st.button("Refresh Templates", on_click=clear_template_cache, key="refresh_templates_btn")
    template_files = list_templates()
    show_template_stats(template_files)
    if not template_files:
        st.warning("No templates found. Please add a template first or check your connection.")
        show_retry_button("gen")
    else:
        # Search box for template name
        search_query = st.text_input("Search template name", "", key="gen_search_box")
        filtered_template_files = [f for f in template_files if search_query.lower() in f.lower()]
        # Recent templates section
        st.markdown("**Recent Templates:**")
        recent_templates = st.session_state.get('recent_templates', [])
        shown_recent = [f for f in recent_templates if f in template_files][:3]
        cols = st.columns(len(shown_recent) if shown_recent else 1)
        selected_recent = None
        for i, f in enumerate(shown_recent):
            if cols[i].button(f, key=f"recent_btn_{f}"):
                selected_recent = f
        # Parse user, skill, and template name from filenames
        user_skill_template_list = [parse_template_info(f) for f in filtered_template_files]
        users = sorted(set(u for u, _, _ in user_skill_template_list))
        skills = sorted(set(s for _, s, _ in user_skill_template_list))
        selected_users = st.multiselect("Filter by User Alias", users, default=users, key="gen_user_filter")
        selected_skills = st.multiselect("Filter by Skill", skills, default=skills, key="gen_skill_filter")
        filtered_indices = [i for i, (u, s, _) in enumerate(user_skill_template_list) if u in selected_users and s in selected_skills]
        if not filtered_indices:
            st.info("No templates match the selected filters.")
        else:
            filtered_files = [filtered_template_files[i] for i in filtered_indices]
            # If a recent template button was clicked, use it as the selected template
            if selected_recent and selected_recent in filtered_files:
                selected_idx = filtered_files.index(selected_recent)
            else:
                selected_idx = st.selectbox("Choose a template", range(len(filtered_files)), format_func=lambda i: filtered_files[i], key="gen_template_select")
            selected_template_file = filtered_files[selected_idx]
            template = load_template(selected_template_file)
            if not template:
                st.error("Could not load the selected template.")
                show_retry_button("gen_load")
            else:
                st.markdown(f"**Template:** {template['name']}")
                st.markdown(f"**Description:** {template.get('description', 'No description provided.')}")
                st.markdown("**Email Preview:**")
                st.code(template['body'], language='markdown')
                st.subheader("Fill in the variables:")
                user_inputs = {}
                for var in template['variables']:
                    user_inputs[var] = st.text_input(f"{var.replace('_', ' ').capitalize()}", key=f"gen_var_{var}")
                def fill_template(body, variables):
                    return body.format(**variables)
                if st.button("Generate Response", key="gen_generate_btn"):
                    try:
                        update_recent_templates(selected_template_file)
                        response = fill_template(template['body'], user_inputs)
                        st.success("Generated Email:")
                        st.text_area("Response", response, height=400, key="gen_response_box")
                        st.code(response, language='markdown')
                        st.write('---')
                        st.download_button("Download as .txt", response, file_name="response.txt", key="gen_download_btn")
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
    template_files = list_templates()
    show_template_stats(template_files)
    st.button("Refresh Templates", on_click=clear_template_cache, key="refresh_templates_btn_add")
    if not template_files:
        st.warning("Could not load templates. Please check your connection.")
        show_retry_button("add")
    template_name = st.text_input("Template Name (e.g., tirshiva_ILAC_reimbursement)", key="add_template_name")
    template_description = st.text_input("Short Description (when to use this template)", key="add_template_description")
    email_body = st.text_area("Paste your email template here. Use {variable} for placeholders.", height=300, key="add_email_body")
    detected_vars = []
    if email_body:
        detected_vars = re.findall(r'\{(.*?)\}', email_body)
        detected_vars = list(dict.fromkeys([v.strip() for v in detected_vars if v.strip()]))  # unique, non-empty
        st.info(f"Detected variables: {', '.join(detected_vars) if detected_vars else 'None'}")
    custom_vars = st.text_input("Edit variables (comma-separated)", value=", ".join(detected_vars), key="add_custom_vars")
    if st.button("Save Template", key="add_save_btn"):
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
            st.rerun()

# --- Tab 3: Edit Template ---
with tabs[2]:
    st.header("Edit an Existing Template")
    st.button("Refresh Templates", on_click=clear_template_cache, key="refresh_templates_btn_edit")
    template_files = list_templates()
    if not template_files:
        st.warning("No templates found to edit or could not load templates. Please check your connection.")
        show_retry_button("edit")
    else:
        selected_template_file = st.selectbox("Select a template to edit", template_files, key="edit_template_select")
        template = load_template(selected_template_file)
        if template is None:
            st.error("Could not load the selected template.")
            show_retry_button("edit_load")
        else:
            # Pre-fill fields
            new_name = st.text_input("Template Name (cannot be changed)", value=selected_template_file.rsplit('.', 1)[0], disabled=True, key="edit_template_name")
            new_description = st.text_input("Short Description (when to use this template)", value=template.get("description", ""), key="edit_template_description")
            new_body = st.text_area("Email body (use {variable} for placeholders)", value=template.get("body", ""), height=300, key="edit_email_body")
            detected_vars = re.findall(r'\{(.*?)\}', new_body)
            detected_vars = list(dict.fromkeys([v.strip() for v in detected_vars if v.strip()]))
            st.info(f"Detected variables: {', '.join(detected_vars) if detected_vars else 'None'}")
            custom_vars = st.text_input("Edit variables (comma-separated)", value=", ".join(detected_vars), key="edit_custom_vars")
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
                    st.rerun() 