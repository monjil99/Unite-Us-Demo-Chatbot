import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
from data_models import Question, FormTemplate, DataManager
import json
from auth import is_authenticated, get_user_templates, get_user_info, show_user_header

def show_admin_interface():
    """Admin interface for business users to manage forms"""
    st.title("🏢 Business Admin - Form Management")
    
    # Show user header with logout option
    show_user_header()
    
    # Add settings panel for admin
    with st.expander("⚙️ Admin Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔑 API Configuration")
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.get('user_api_key', ''),
                help="Enter your OpenAI API key for testing admin features.",
                placeholder="sk-..."
            )
            if api_key:
                st.session_state.user_api_key = api_key
                st.success("✅ API key configured")
        
        with col2:
            st.markdown("#### 🤖 Model Selection")
            model_options = [
                "gpt-4o-mini",
                "gpt-4o", 
                "gpt-4",
                "gpt-4-turbo",
                "o1-mini",
                "o1-preview"
            ]
            selected_model = st.selectbox(
                "OpenAI Model",
                options=model_options,
                index=0,
                help="Choose the OpenAI model for admin operations"
            )
            st.session_state.selected_model = selected_model
    
    st.markdown("---")
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    
    # Sidebar navigation
    st.sidebar.title("Admin Navigation")
    
    # Check if we have a session state page override
    if hasattr(st.session_state, 'admin_page') and st.session_state.admin_page:
        default_page = st.session_state.admin_page
    else:
        default_page = "View Templates"
    
    admin_page = st.sidebar.selectbox(
        "Choose Action",
        ["View Templates", "View Applications", "Create New Template", "Edit Template", "Manage Questions"],
        index=["View Templates", "View Applications", "Create New Template", "Edit Template", "Manage Questions"].index(default_page) if default_page in ["View Templates", "View Applications", "Create New Template", "Edit Template", "Manage Questions"] else 0
    )
    
    # Update session state
    st.session_state.admin_page = admin_page
    
    if admin_page == "View Templates":
        show_templates_overview(data_manager)
    elif admin_page == "View Applications":
        show_submitted_applications(data_manager)
    elif admin_page == "Create New Template":
        create_new_template(data_manager)
    elif admin_page == "Edit Template":
        edit_existing_template(data_manager)
    elif admin_page == "Manage Questions":
        manage_questions(data_manager)

def show_templates_overview(data_manager):
    """Show overview of form templates accessible to current user with version management"""
    st.header("📋 Your Form Templates")
    
    user_info = get_user_info()
    user_templates = get_user_templates()
    
    # Get all template versions for this organization
    template_versions = data_manager.get_template_versions(user_info['business_name'])
    
    if not template_versions:
        st.warning(f"No templates found for {user_info['business_name']}. Create a new template to get started.")
        return
    
    st.info(f"Showing templates for: **{user_info['business_name']}**")
    
    # Group templates by base template
    template_groups = {}
    for template in template_versions:
        base_id = template.base_template_id or template.id
        if base_id not in template_groups:
            template_groups[base_id] = []
        template_groups[base_id].append(template)
    
    # Display template groups
    for base_id, versions in template_groups.items():
        # Sort versions by version number (newest first)
        versions.sort(key=lambda x: x.version, reverse=True)
        active_version = next((v for v in versions if v.is_active), versions[0])
        
        with st.expander(f"📄 {active_version.name} (Active: v{active_version.version})", expanded=True):
            # Show active version details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Organization:** {active_version.organization}")
                st.write(f"**Questions:** {len(active_version.questions)}")
                st.write(f"**Description:** {active_version.description}")
                st.write(f"**Active Version:** {active_version.version}")
                st.write(f"**Last Updated:** {active_version.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                # Template actions
                if st.button(f"Preview Active", key=f"preview_{active_version.id}"):
                    st.session_state.preview_template = active_version.id
                    st.rerun()
                
                if st.button(f"Edit (New Version)", key=f"edit_{active_version.id}"):
                    st.session_state.edit_template = active_version.id
                    st.session_state.admin_page = "Edit Template"
                    st.rerun()
            
            # Show all versions
            st.subheader("📊 Version History")
            
            for version in versions:
                status = "🟢 ACTIVE" if version.is_active else "⚪ Inactive"
                created_str = version.created_at.strftime('%Y-%m-%d %H:%M')
                
                version_col1, version_col2, version_col3, version_col4 = st.columns([1, 2, 2, 1])
                
                with version_col1:
                    st.write(f"**v{version.version}**")
                
                with version_col2:
                    st.write(f"{status}")
                
                with version_col3:
                    st.write(f"Created: {created_str}")
                
                with version_col4:
                    if not version.is_active:
                        if st.button(f"Activate", key=f"activate_{version.id}"):
                            data_manager.set_active_template(version.id)
                            st.success(f"Version {version.version} is now active!")
                            st.rerun()
            
            st.markdown("---")
    
    # Show preview if selected
    if hasattr(st.session_state, 'preview_template') and st.session_state.preview_template:
        st.markdown("---")
        preview_template(data_manager, st.session_state.preview_template)
        
        # Clear preview button
        if st.button("❌ Close Preview", key="close_preview"):
            del st.session_state.preview_template
            st.rerun()

def preview_template(data_manager, template_id):
    """Preview a template by ID"""
    # Find template by ID
    template = None
    for tmpl in data_manager.get_all_templates().values():
        if tmpl.id == template_id:
            template = tmpl
            break
    
    if not template:
        st.error("Template not found!")
        return
    
    st.header(f"📖 Preview: {template.name}")
    
    st.write(f"**Organization:** {template.organization}")
    st.write(f"**Description:** {template.description}")
    st.write(f"**Total Questions:** {len(template.questions)}")
    
    st.subheader("Questions:")
    for i, question in enumerate(template.questions, 1):
        with st.expander(f"Question {i}: {question.question_text[:50]}..."):
            st.write(f"**Full Question:** {question.question_text}")
            st.write(f"**Field Type:** {question.field_type}")
            st.write(f"**Required:** {'Yes' if question.required else 'No'}")
            
            if question.field_responses:
                st.write("**Response Options:**")
                for response in question.field_responses:
                    st.write(f"• {response}")
            
            if question.help_text:
                st.write(f"**Help Text:** {question.help_text}")
            
            if question.conditional_logic:
                st.write(f"**Conditional Logic:** {question.conditional_logic}")

def create_new_template(data_manager):
    """Create a new form template"""
    st.header("➕ Create New Form Template")
    
    user_info = get_user_info()
    st.info(f"Creating template for: **{user_info['business_name']}**")
    
    with st.form("new_template_form"):
        st.subheader("Basic Information")
        
        template_name = st.text_input("Template Name*", placeholder="e.g., Community Health Intake Form")
        organization = st.text_input("Organization*", value=user_info['business_name'], placeholder="e.g., Community Health Center")
        description = st.text_area("Description", placeholder="Brief description of this form's purpose")
        
        st.subheader("Questions")
        st.write("Add questions for your form:")
        
        # Initialize questions in session state
        if 'new_template_questions' not in st.session_state:
            st.session_state.new_template_questions = []
        
        # Add question button
        if st.form_submit_button("Add Question"):
            st.session_state.new_template_questions.append({
                'id': str(uuid.uuid4()),
                'question_text': '',
                'field_type': 'text',
                'field_responses': [],
                'required': True,
                'help_text': ''
            })
            st.rerun()
        
        # Display existing questions
        for i, q in enumerate(st.session_state.new_template_questions):
            st.write(f"**Question {i+1}**")
            
            q['question_text'] = st.text_input(f"Question Text {i+1}", value=q['question_text'], key=f"q_text_{i}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                field_types = ['text', 'email', 'phone', 'date', 'number', 'dropdown', 'drop down-single select', 'checkbox', 'radio', 'single select', 'multi select']
                # Handle field type compatibility
                current_type = q['field_type']
                if current_type not in field_types:
                    if 'drop' in current_type.lower():
                        current_type = 'dropdown'
                    elif 'single' in current_type.lower():
                        current_type = 'single select'
                    elif 'multi' in current_type.lower():
                        current_type = 'multi select'
                    else:
                        current_type = 'text'
                
                q['field_type'] = st.selectbox(
                    f"Field Type {i+1}",
                    field_types,
                    index=field_types.index(current_type),
                    key=f"q_type_{i}"
                )
            
            with col_b:
                q['required'] = st.checkbox(f"Required {i+1}", value=q['required'], key=f"q_req_{i}")
            
            if q['field_type'] in ['dropdown', 'checkbox', 'radio']:
                responses_text = st.text_area(
                    f"Response Options {i+1} (one per line)",
                    value='\n'.join(q['field_responses']),
                    key=f"q_resp_{i}"
                )
                q['field_responses'] = [r.strip() for r in responses_text.split('\n') if r.strip()]
            
            q['help_text'] = st.text_input(f"Help Text {i+1}", value=q['help_text'], key=f"q_help_{i}")
            
            st.markdown("---")
        
        # Submit template
        submitted = st.form_submit_button("Create Template")
        
        if submitted:
            if not template_name or not organization:
                st.error("Please fill in all required fields (marked with *)")
            elif not st.session_state.new_template_questions:
                st.error("Please add at least one question to the template")
            else:
                # Create questions
                questions = []
                for i, q_data in enumerate(st.session_state.new_template_questions):
                    question = Question(
                        id=q_data['id'],
                        number=i+1,
                        question_text=q_data['question_text'],
                        field_type=q_data['field_type'],
                        field_responses=q_data['field_responses'],
                        required=q_data['required'],
                        help_text=q_data['help_text']
                    )
                    questions.append(question)
                
                # Create template
                template = FormTemplate(
                    id=str(uuid.uuid4()),
                    name=template_name,
                    organization=organization,
                    description=description,
                    questions=questions,
                    standard_fields=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    version=1,
                    base_template_id=None,
                    is_active=True
                )
                
                # Save template
                data_manager.save_template(template)
                
                st.success(f"Template '{template_name}' created successfully!")
                st.session_state.new_template_questions = []
                st.rerun()
    
    # Question management outside the form
    if st.session_state.new_template_questions:
        st.subheader("📝 Manage Questions")
        st.write("Click to remove questions from your template:")
        
        cols = st.columns(3)
        for i, q in enumerate(st.session_state.new_template_questions):
            with cols[i % 3]:
                question_preview = q['question_text'][:30] + "..." if len(q['question_text']) > 30 else q['question_text']
                if st.button(f"❌ Remove Q{i+1}: {question_preview}", key=f"remove_new_{i}"):
                    st.session_state.new_template_questions.pop(i)
                    st.rerun()

def edit_existing_template(data_manager):
    """Edit an existing template"""
    st.header("✏️ Edit Existing Template")
    
    # Get user's accessible templates
    user_info = get_user_info()
    template_versions = data_manager.get_template_versions(user_info['business_name'])
    
    if not template_versions:
        st.warning(f"No templates available to edit for {user_info['business_name']}.")
        return
    
    # Get active templates only for selection
    active_templates = [t for t in template_versions if t.is_active]
    
    if not active_templates:
        st.warning("No active templates found. Please activate a template version first.")
        return
    
    # Template selection
    template_options = [(f"{t.name} (v{t.version})", t.id) for t in active_templates]
    template_names = [opt[0] for opt in template_options]
    template_ids = [opt[1] for opt in template_options]
    
    # Check if we have a pre-selected template from button click
    default_idx = 0
    if hasattr(st.session_state, 'edit_template') and st.session_state.edit_template in template_ids:
        default_idx = template_ids.index(st.session_state.edit_template)
        # Clear the session state after using it
        del st.session_state.edit_template
    
    selected_idx = st.selectbox("Select Template to Edit", range(len(template_names)), 
                               format_func=lambda x: template_names[x], index=default_idx)
    selected_template_id = template_ids[selected_idx]
    template = next(t for t in active_templates if t.id == selected_template_id)
    
    st.subheader(f"Editing: {template.name}")
    
    # Edit form
    with st.form("edit_template_form"):
        template_name = st.text_input("Template Name", value=template.name)
        organization = st.text_input("Organization", value=template.organization)
        description = st.text_area("Description", value=template.description)
        
        st.subheader("Questions")
        
        # Load questions into session state for editing
        session_key = f'edit_questions_{selected_template_id}'
        if session_key not in st.session_state:
            st.session_state[session_key] = [
                {
                    'id': q.id,
                    'question_text': q.question_text,
                    'field_type': q.field_type,
                    'field_responses': q.field_responses,
                    'required': q.required,
                    'help_text': q.help_text or ''
                }
                for q in template.questions
            ]
        
        questions_data = st.session_state[session_key]
        
        # Add question button
        if st.form_submit_button("Add Question"):
            questions_data.append({
                'id': str(uuid.uuid4()),
                'question_text': '',
                'field_type': 'text',
                'field_responses': [],
                'required': True,
                'help_text': ''
            })
            st.rerun()
        
        # Display and edit questions
        for i, q in enumerate(questions_data):
            st.write(f"**Question {i+1}**")
            
            q['question_text'] = st.text_input(f"Question Text {i+1}", value=q['question_text'], key=f"edit_q_text_{i}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                field_types = ['text', 'email', 'phone', 'date', 'number', 'dropdown', 'drop down-single select', 'checkbox', 'radio', 'single select', 'multi select']
                # Handle field type compatibility
                current_type = q['field_type']
                if current_type not in field_types:
                    if 'drop' in current_type.lower():
                        current_type = 'dropdown'
                    elif 'single' in current_type.lower():
                        current_type = 'single select'
                    elif 'multi' in current_type.lower():
                        current_type = 'multi select'
                    else:
                        current_type = 'text'
                
                q['field_type'] = st.selectbox(
                    f"Field Type {i+1}",
                    field_types,
                    index=field_types.index(current_type),
                    key=f"edit_q_type_{i}"
                )
            
            with col_b:
                q['required'] = st.checkbox(f"Required {i+1}", value=q['required'], key=f"edit_q_req_{i}")
            
            if q['field_type'] in ['dropdown', 'checkbox', 'radio']:
                responses_text = st.text_area(
                    f"Response Options {i+1} (one per line)",
                    value='\n'.join(q['field_responses']),
                    key=f"edit_q_resp_{i}"
                )
                q['field_responses'] = [r.strip() for r in responses_text.split('\n') if r.strip()]
            
            q['help_text'] = st.text_input(f"Help Text {i+1}", value=q['help_text'], key=f"edit_q_help_{i}")
            
            st.markdown("---")
        
        # Save changes
        if st.form_submit_button("Save Changes"):
            if not template_name or not organization:
                st.error("Please fill in all required fields")
            else:
                # Create new version of template
                questions = []
                for i, q_data in enumerate(questions_data):
                    question = Question(
                        id=q_data['id'],
                        number=i+1,
                        question_text=q_data['question_text'],
                        field_type=q_data['field_type'],
                        field_responses=q_data['field_responses'],
                        required=q_data['required'],
                        help_text=q_data['help_text']
                    )
                    questions.append(question)
                
                # Create new template version
                new_template = FormTemplate(
                    id=str(uuid.uuid4()),
                    name=template_name,
                    organization=organization,
                    description=description,
                    questions=questions,
                    standard_fields=template.standard_fields,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    version=template.version + 1,
                    base_template_id=template.base_template_id or template.id,
                    is_active=True
                )
                
                data_manager.save_template(new_template)
                st.success(f"New template version {new_template.version} created successfully!")
                
                # Clear the session state for this template
                if session_key in st.session_state:
                    del st.session_state[session_key]
                st.rerun()
    
    # Question management outside the form
    if session_key in st.session_state and st.session_state[session_key]:
        st.subheader("📝 Manage Questions")
        st.write("Click to remove questions from your template:")
        
        cols = st.columns(3)
        questions_data = st.session_state[session_key]
        for i, q in enumerate(questions_data):
            with cols[i % 3]:
                question_preview = q['question_text'][:30] + "..." if len(q['question_text']) > 30 else q['question_text']
                if st.button(f"❌ Remove Q{i+1}: {question_preview}", key=f"remove_edit_{i}"):
                    questions_data.pop(i)
                    st.rerun()

def manage_questions(data_manager):
    """Manage questions across templates"""
    st.header("❓ Question Management")
    
    templates = data_manager.get_all_templates()
    if not templates:
        st.warning("No templates available.")
        return
    
    # Show all questions from all templates
    st.subheader("All Questions Across Templates")
    
    all_questions = []
    for template_key, template in templates.items():
        for question in template.questions:
            all_questions.append({
                'Template': template.name,
                'Question': question.question_text,
                'Type': question.field_type,
                'Required': question.required,
                'Help Text': question.help_text or 'N/A'
            })
    
    if all_questions:
        df = pd.DataFrame(all_questions)
        st.dataframe(df, use_container_width=True)
        
        # Export questions
        if st.button("Export Questions to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"form_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No questions found in any template.")

def show_submitted_applications(data_manager):
    """Show submitted applications for the current organization"""
    from auth import get_user_info
    
    st.header("📝 Submitted Applications")
    
    # Get current user's organization
    user_info = get_user_info()
    if not user_info:
        st.error("Unable to get user information")
        return
    
    organization = user_info['business_name']
    st.subheader(f"Applications for: {organization}")
    
    # Get applications for this organization
    org_filter = organization.lower().replace(" ", "_")
    applications = data_manager.get_submitted_applications(org_filter)
    
    if not applications:
        st.info("No applications have been submitted yet.")
        return
    
    # Display applications
    st.write(f"**Total Applications:** {len(applications)}")
    
    # Add filters
    col1, col2 = st.columns([1, 1])
    with col1:
        date_filter = st.selectbox(
            "Filter by Date",
            ["All Time", "Today", "This Week", "This Month"],
            key="app_date_filter"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "New", "Processed", "Completed"],
            key="app_status_filter"
        )
    
    # Filter applications based on selections
    filtered_apps = applications.copy()
    
    if date_filter != "All Time":
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if date_filter == "Today":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "This Week":
            cutoff = now - timedelta(days=7)
        elif date_filter == "This Month":
            cutoff = now - timedelta(days=30)
        
        filtered_apps = [
            app for app in filtered_apps
            if datetime.fromisoformat(app.get('submission_date', '')) >= cutoff
        ]
    
    # Display each application
    for i, app in enumerate(filtered_apps):
        with st.expander(
            f"Application #{i+1} - {app.get('assistance_request_id', 'Unknown ID')} "
            f"(Submitted: {app.get('submission_date', 'Unknown Date')[:10]})"
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Application Details:**")
                st.write(f"• **ID:** {app.get('assistance_request_id', 'N/A')}")
                st.write(f"• **Form:** {app.get('form_id', 'N/A')}")
                st.write(f"• **Submitted:** {app.get('submission_date', 'N/A')[:16]}")
                st.write(f"• **Description:** {app.get('description', 'N/A')}")
                
                # Personal Information
                personal_info = app.get('personal_info', {})
                if personal_info and any(personal_info.values()):
                    st.write("**Personal Information:**")
                    if personal_info.get('person_first_name') or personal_info.get('person_last_name'):
                        name = f"{personal_info.get('person_first_name', '')} {personal_info.get('person_last_name', '')}".strip()
                        st.write(f"• **Name:** {name}")
                    if personal_info.get('person_email_address'):
                        st.write(f"• **Email:** {personal_info.get('person_email_address')}")
                    if personal_info.get('person_phone_number'):
                        st.write(f"• **Phone:** {personal_info.get('person_phone_number')}")
                
                # Custom Responses
                custom_responses = app.get('custom_responses', {})
                if custom_responses:
                    st.write("**Responses:**")
                    for question_id, response in custom_responses.items():
                        st.write(f"• **{question_id}:** {response}")
            
            with col2:
                st.write("**Actions:**")
                
                # Download individual application
                if st.button(f"📥 Download JSON", key=f"download_{i}"):
                    import json
                    json_str = json.dumps(app, indent=2)
                    st.download_button(
                        label="Download Application JSON",
                        data=json_str,
                        file_name=f"application_{app.get('assistance_request_id', i)}.json",
                        mime="application/json",
                        key=f"download_json_{i}"
                    )
                
                # Mark as processed (future feature)
                if st.button(f"✅ Mark as Processed", key=f"process_{i}"):
                    st.success("Marked as processed!")
                    # TODO: Add actual status update functionality
    
    # Bulk download option
    if filtered_apps:
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📊 Export All to CSV"):
                # Convert applications to CSV format
                import pandas as pd
                
                csv_data = []
                for app in filtered_apps:
                    row = {
                        'Application_ID': app.get('assistance_request_id', ''),
                        'Form_ID': app.get('form_id', ''),
                        'Submission_Date': app.get('submission_date', ''),
                        'Description': app.get('description', ''),
                        'First_Name': app.get('personal_info', {}).get('person_first_name', ''),
                        'Last_Name': app.get('personal_info', {}).get('person_last_name', ''),
                        'Email': app.get('personal_info', {}).get('person_email_address', ''),
                        'Phone': app.get('personal_info', {}).get('person_phone_number', ''),
                    }
                    
                    # Add custom responses as separate columns
                    custom_responses = app.get('custom_responses', {})
                    for question_id, response in custom_responses.items():
                        row[f'Response_{question_id}'] = response
                    
                    csv_data.append(row)
                
                df = pd.DataFrame(csv_data)
                csv_string = df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV Report",
                    data=csv_string,
                    file_name=f"{organization.replace(' ', '_')}_applications_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📦 Export All to JSON"):
                import json
                json_string = json.dumps(filtered_apps, indent=2)
                
                st.download_button(
                    label="Download JSON Report",
                    data=json_string,
                    file_name=f"{organization.replace(' ', '_')}_applications_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    show_admin_interface()
