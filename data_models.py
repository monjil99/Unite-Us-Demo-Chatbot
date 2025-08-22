import pandas as pd
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os

@dataclass
class Question:
    """Represents a single question in the intake form"""
    id: str
    number: int
    question_text: str
    field_type: str
    field_responses: List[str]
    conditional_logic: Optional[str] = None
    required: bool = True
    validation_pattern: Optional[str] = None
    help_text: Optional[str] = None

@dataclass
class FormTemplate:
    """Represents a complete form template for an organization"""
    id: str
    name: str
    organization: str
    description: str
    questions: List[Question]
    standard_fields: List[str]
    created_at: datetime
    updated_at: datetime
    version: int = 1
    base_template_id: Optional[str] = None
    is_active: bool = True

@dataclass
class PersonalInfo:
    """Standard personal information fields"""
    person_first_name: Optional[str] = None
    person_last_name: Optional[str] = None
    person_date_of_birth: Optional[str] = None
    person_middle_name: Optional[str] = None
    person_preferred_name: Optional[str] = None
    person_gender: Optional[str] = None
    person_citizenship: Optional[str] = None
    person_ethnicity: Optional[str] = None
    person_marital_status: Optional[str] = None
    person_race: Optional[str] = None
    person_phone_number: Optional[str] = None
    person_email_address: Optional[str] = None

@dataclass
class AddressInfo:
    """Address information fields"""
    address_type: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_country: Optional[str] = None
    address_postal_code: Optional[str] = None

@dataclass
class AssistanceRequest:
    """Complete assistance request submission"""
    assistance_request_id: str
    description: str
    service_id: str
    provider_id: str
    case_id: str
    form_id: str
    personal_info: PersonalInfo
    address_info: AddressInfo
    custom_responses: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class DataManager:
    """Manages data operations for the intake system"""
    
    def __init__(self, sample_data_dir: str = "Sample Data"):
        self.sample_data_dir = sample_data_dir
        self.templates = {}
        self.load_templates_from_excel()
    
    def load_templates_from_excel(self):
        """Load form templates from Excel files"""
        excel_files = {
            "broomfield": "Broomfield Department of Health ARF - no PII.xlsx",
            "first_things_first": "First Things First - Dads_Moms - ARF - no PII.xlsx",
            "gateway_ymca": "Gateway YMCA ARF - no PII.xlsx",
            "sbnj_mobile": "SBNJ Mobile Midwife Clinic ARF - NO PII.xlsx"
        }
        
        for org_key, filename in excel_files.items():
            file_path = os.path.join(self.sample_data_dir, filename)
            if os.path.exists(file_path):
                template = self._create_template_from_excel(file_path, org_key)
                self.templates[org_key] = template
    
    def _create_template_from_excel(self, file_path: str, org_key: str) -> FormTemplate:
        """Create a form template from Excel file"""
        try:
            # Read questions sheet
            questions_df = pd.read_excel(file_path, sheet_name=0)  # First sheet
            
            questions = []
            current_question = None
            question_responses = []
            
            question_counter = 1
            for _, row in questions_df.iterrows():
                if pd.notna(row.iloc[0]):  # Question Number column
                    # Save previous question if exists
                    if current_question:
                        questions.append(Question(
                            id=str(uuid.uuid4()),
                            number=current_question['number'],
                            question_text=current_question['text'],
                            field_type=current_question['type'],
                            field_responses=question_responses.copy(),
                            conditional_logic=current_question.get('logic'),
                            help_text=self._generate_help_text(current_question['text'], current_question['type'])
                        ))
                        question_counter += 1
                    
                    # Parse question number safely
                    try:
                        question_num = int(float(str(row.iloc[0])))
                    except (ValueError, TypeError):
                        question_num = question_counter
                    
                    # Start new question
                    current_question = {
                        'number': question_num,
                        'text': row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else "",
                        'type': row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else "text",
                        'logic': row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else None
                    }
                    question_responses = []
                    
                    # Add response if present in same row
                    if len(row) > 4 and pd.notna(row.iloc[4]):
                        question_responses.append(str(row.iloc[4]))
                
                elif current_question and len(row) > 4 and pd.notna(row.iloc[4]):
                    # Additional response for current question
                    question_responses.append(str(row.iloc[4]))
            
            # Don't forget the last question
            if current_question:
                questions.append(Question(
                    id=str(uuid.uuid4()),
                    number=current_question['number'],
                    question_text=current_question['text'],
                    field_type=current_question['type'],
                    field_responses=question_responses.copy(),
                    conditional_logic=current_question.get('logic'),
                    help_text=self._generate_help_text(current_question['text'], current_question['type'])
                ))
            
            # Standard fields from ARF Standard Responses
            standard_fields = [
                "assistance_request_id", "description", "service_id", "provider_id", "case_id",
                "person_first_name", "person_last_name", "person_date_of_birth", "person_gender",
                "person_ethnicity", "person_race", "person_phone_number", "person_email_address",
                "address_line_1", "address_city", "address_state", "address_postal_code"
            ]
            
            org_names = {
                "broomfield": "Broomfield Department of Health",
                "first_things_first": "First Things First - Dads/Moms",
                "gateway_ymca": "Gateway YMCA Community Health",
                "sbnj_mobile": "SBNJ Mobile Midwife Clinic"
            }
            
            return FormTemplate(
                id=str(uuid.uuid4()),
                name=f"{org_names.get(org_key, org_key)} - Assistance Request",
                organization=org_names.get(org_key, org_key),
                description=f"Intake form for {org_names.get(org_key, org_key)}",
                questions=questions,
                standard_fields=standard_fields,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
        except Exception as e:
            print(f"Error creating template from {file_path}: {e}")
            return self._create_default_template(org_key)
    
    def _generate_help_text(self, question_text: str, field_type: str) -> str:
        """Generate helpful explanations for why questions are asked"""
        help_texts = {
            "city": "We need your city to connect you with local resources and services in your area.",
            "phone": "Your phone number helps us contact you about available services and appointments.",
            "email": "Email allows us to send you important updates and resources.",
            "program": "Knowing which programs you're interested in helps us provide targeted assistance.",
            "benefit": "This information helps us understand your current support level and identify additional resources.",
            "contact": "Alternative contact methods ensure we can reach you when primary methods aren't available.",
            "language": "We want to communicate with you in your preferred language for better service.",
            "transportation": "Understanding your transportation needs helps us connect you with mobility resources.",
            "health": "Health information helps us refer you to appropriate medical and wellness services.",
            "urgent": "Identifying urgent needs helps us prioritize your case and provide immediate assistance.",
            "income": "Income information helps determine eligibility for various assistance programs.",
            "housing": "Housing status helps us identify if you need shelter or housing assistance."
        }
        
        question_lower = question_text.lower()
        for key, help_text in help_texts.items():
            if key in question_lower:
                return help_text
        
        return "This information helps us better understand your needs and connect you with appropriate resources."
    
    def _create_default_template(self, org_key: str) -> FormTemplate:
        """Create a default template if Excel parsing fails"""
        return FormTemplate(
            id=str(uuid.uuid4()),
            name=f"{org_key} - Default Template",
            organization=org_key,
            description=f"Default template for {org_key}",
            questions=[],
            standard_fields=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def get_template(self, org_key: str) -> Optional[FormTemplate]:
        """Get template by organization key"""
        return self.templates.get(org_key)
    
    def get_all_templates(self) -> Dict[str, FormTemplate]:
        """Get all available templates"""
        return self.templates
    
    def save_template(self, template: FormTemplate):
        """Save a template with versioning"""
        org_key = template.organization.lower().replace(" ", "_")
        
        # If this is an update to existing template, create new version
        if org_key in self.templates and template.base_template_id:
            # Deactivate the old version
            old_template = self.templates[org_key]
            old_template.is_active = False
            
            # Find the highest version number for this organization
            max_version = 1
            for key, tmpl in self.templates.items():
                if (tmpl.organization == template.organization and 
                    (tmpl.base_template_id == template.base_template_id or tmpl.id == template.base_template_id)):
                    max_version = max(max_version, tmpl.version)
            
            # Set version number for new template
            template.version = max_version + 1
            
            # Create unique key with version
            versioned_key = f"{org_key}_v{template.version}"
            self.templates[versioned_key] = template
            
            # Keep the original key pointing to latest active version
            self.templates[org_key] = template
        else:
            # New template
            template.version = 1
            template.is_active = True
            self.templates[org_key] = template
    
    def get_template_versions(self, organization: str) -> List[FormTemplate]:
        """Get all versions of templates for an organization"""
        org_key = organization.lower().replace(" ", "_")
        versions = []
        
        for key, template in self.templates.items():
            if template.organization == organization:
                versions.append(template)
        
        # Sort by version number, newest first
        return sorted(versions, key=lambda x: x.version, reverse=True)
    
    def set_active_template(self, template_id: str):
        """Set a specific template version as active"""
        target_template = None
        
        # Find the template by ID
        for template in self.templates.values():
            if template.id == template_id:
                target_template = template
                break
        
        if not target_template:
            return False
        
        # Deactivate all versions for this organization
        for template in self.templates.values():
            if template.organization == target_template.organization:
                template.is_active = False
        
        # Activate the selected version
        target_template.is_active = True
        
        # Update the main organization key to point to active version
        org_key = target_template.organization.lower().replace(" ", "_")
        self.templates[org_key] = target_template
        
        return True
    
    def save_response_to_excel(self, response: AssistanceRequest, output_file: str):
        """Save response to Excel format matching original structure"""
        try:
            # Create standard responses data
            standard_data = {
                'assistance_request_id': [response.assistance_request_id],
                'description': [response.description],
                'service_id': [response.service_id],
                'provider_id': [response.provider_id],
                'case_id': [response.case_id],
                'form_id': [response.form_id],
                'created_at': [response.created_at],
                'updated_at': [response.updated_at]
            }
            
            # Add personal info
            personal_dict = asdict(response.personal_info)
            for key, value in personal_dict.items():
                standard_data[key] = [value]
            
            # Add address info
            address_dict = asdict(response.address_info)
            for key, value in address_dict.items():
                standard_data[key] = [value]
            
            # Create DataFrames
            standard_df = pd.DataFrame(standard_data)
            
            # Custom responses
            custom_data = []
            for question_id, answer in response.custom_responses.items():
                custom_data.append({
                    'form_id': response.form_id,
                    'submission_id': response.assistance_request_id,
                    'question_id': question_id,
                    'response_value': answer,
                    'created_at': response.created_at,
                    'updated_at': response.updated_at
                })
            
            custom_df = pd.DataFrame(custom_data)
            
            # Write to Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                standard_df.to_excel(writer, sheet_name='Standard Responses', index=False)
                custom_df.to_excel(writer, sheet_name='Custom Responses', index=False)
            
            print(f"Response saved to {output_file}")
            
        except Exception as e:
            print(f"Error saving to Excel: {e}")
    
    def save_response_to_json(self, response: AssistanceRequest, output_file: str):
        """Save response to JSON format"""
        try:
            response_dict = asdict(response)
            # Convert datetime objects to strings
            response_dict['created_at'] = response.created_at.isoformat()
            response_dict['updated_at'] = response.updated_at.isoformat()
            
            with open(output_file, 'w') as f:
                json.dump(response_dict, f, indent=2)
            
            print(f"Response saved to {output_file}")
            
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def save_submitted_application(self, response: AssistanceRequest):
        """Save submitted application for admin viewing"""
        try:
            # Ensure submissions directory exists
            submissions_dir = "submissions"
            os.makedirs(submissions_dir, exist_ok=True)
            
            # Load existing submissions or create new list
            submissions_file = f"{submissions_dir}/submitted_applications.json"
            submitted_applications = []
            
            if os.path.exists(submissions_file):
                try:
                    with open(submissions_file, 'r') as f:
                        submitted_applications = json.load(f)
                except:
                    submitted_applications = []
            
            # Convert response to dict
            response_dict = asdict(response)
            response_dict['created_at'] = response.created_at.isoformat()
            response_dict['updated_at'] = response.updated_at.isoformat()
            response_dict['submission_date'] = datetime.now().isoformat()
            
            # Add to submissions list
            submitted_applications.append(response_dict)
            
            # Save updated list
            with open(submissions_file, 'w') as f:
                json.dump(submitted_applications, f, indent=2)
                
            print(f"Application saved for admin viewing: {response.assistance_request_id}")
            
        except Exception as e:
            print(f"Error saving submitted application: {e}")
    
    def get_submitted_applications(self, organization_filter: Optional[str] = None) -> List[Dict]:
        """Get submitted applications, optionally filtered by organization"""
        try:
            submissions_file = "submissions/submitted_applications.json"
            
            if not os.path.exists(submissions_file):
                return []
            
            with open(submissions_file, 'r') as f:
                applications = json.load(f)
            
            # Filter by organization if specified
            if organization_filter:
                org_filter = organization_filter.lower()
                applications = [
                    app for app in applications 
                    if app.get('provider_id', '').lower() == org_filter or
                       app.get('form_id', '').lower().startswith(org_filter)
                ]
            
            # Sort by submission date (newest first)
            applications.sort(key=lambda x: x.get('submission_date', ''), reverse=True)
            
            return applications
            
        except Exception as e:
            print(f"Error loading submitted applications: {e}")
            return []
