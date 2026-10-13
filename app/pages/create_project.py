import streamlit as st
from app.database.connection import get_db
from app.services.project_service import ProjectService
from app.utils.config_loader import load_config
from app.components.forms import render_dynamic_form, validate_dynamic_form

st.title("Create New Project")

project_fields_config = load_config('project_fields')['fields']

if 'created_project_code' not in st.session_state:
    st.session_state.created_project_code = None
    st.session_state.created_project_id = None

if st.session_state.created_project_code:
    st.success("### Project Created Successfully")
    st.markdown(f"**Project ID:** `{st.session_state.created_project_id}`")
    st.markdown(f"**Project Access Code:** `{st.session_state.created_project_code}`")
    st.warning("Save this code securely. You will need your Project ID and this code to edit your project in the future. It will not be shown again.")
    if st.button("Create Another Project"):
        st.session_state.created_project_code = None
        st.session_state.created_project_id = None
        st.rerun()
else:
    with st.form("create_project_form"):
        form_data = render_dynamic_form(project_fields_config)
        submitted = st.form_submit_button("Create Project")
        
        if submitted:
            errors = validate_dynamic_form(project_fields_config, form_data)
            project_id = form_data.get('project_id')
            if not project_id:
                errors.append("Project ID is required.")
                
            if errors:
                for error in errors:
                    st.error(error)
            else:
                db = next(get_db())
                # Check if exists
                existing = ProjectService.get_project(db, project_id)
                if existing:
                    st.error(f"Project with ID {project_id} already exists.")
                else:
                    try:
                        project, access_code = ProjectService.create_project(db, project_id, form_data, "PublicUser") # In real app, user would be captured if Entra ID was used
                        st.session_state.created_project_code = access_code
                        st.session_state.created_project_id = project_id
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating project: {str(e)}")
