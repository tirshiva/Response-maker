# Response Maker

A Streamlit app to generate professional email responses from customizable templates with variable fields.

## Features
- Easy template management: Add, categorize, and use templates from the web interface.
- Smart variable detection: Just paste your email content; variables are auto-detected.
- Filtering: Find templates by user alias and skill.
- Copy/download responses instantly.

## Who can use this?
**You can add and use templates!**

## Template Naming Convention
- Name your template as `[useralias]_[skill]_[shortdescription]` (e.g., `tirshiva_ILAC_reimbursement`).
- This helps categorize templates by user and skill.
- Add a short description of when the template should be used (e.g., "When investigation is completed and reimbursement is required").

## How to Use
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. **Add a new template:**
   - Go to the "Add New Template" tab.
   - Enter the template name, short description, and email body (use `{variable}` for placeholders).
   - Save. Your template is now available to all users.
4. **Generate a response:**
   - Go to the "Generate Response" tab.
   - Filter/search for a template, fill in the variables, and copy/download your response.

## Example Use Case
- "tirshiva_ILAC_reimbursement": When investigation is completed and reimbursement is required.

## Notes
- All templates are shared and visible to all users.
- Please follow the naming convention for easy organization.

## Usage
- Add your email templates in the `templates/` folder as JSON files.
- Launch the app, select a template, fill in the variables, and generate your response! 