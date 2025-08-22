import openai
from typing import Dict, List, Optional, Any, Tuple
import json
import re
from datetime import datetime
from data_models import Question, FormTemplate, AssistanceRequest, PersonalInfo, AddressInfo
import config

class ChatbotEngine:
    """AI-powered chatbot for interactive form filling using GPT-4o mini for all intelligence"""
    
    def __init__(self):
        # Lazy load API key when initializing the client
        api_key = config.get_openai_api_key()
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.conversation_history = []
        self.current_question = None
        self.current_template = None
        self.responses = {}
        self.personal_info = PersonalInfo()
        self.address_info = AddressInfo()
    
    def get_selected_model(self):
        """Get the selected OpenAI model from session state"""
        try:
            import streamlit as st
            return st.session_state.get('selected_model', 'gpt-4o-mini')
        except (ImportError, AttributeError):
            return 'gpt-4o-mini'  # Default fallback
    
    def start_conversation(self, template: FormTemplate) -> str:
        """Start a new conversation with a form template"""
        self.current_template = template
        self.conversation_history = []
        self.responses = {}
        self.personal_info = PersonalInfo()
        self.address_info = AddressInfo()
        
        welcome_message = f"""
        Hello! I'm here to help you complete the {template.name} intake form. 
        
        I'll ask you questions one at a time in a conversational way. If you're unsure about any question, 
        just ask "Why do you need this?" and I'll explain. 
        
        Let's get started!
        """
        
        return welcome_message.strip()
    
    def get_next_question(self) -> Optional[str]:
        """Get the next question to ask, considering branching logic"""
        if not self.current_template:
            return None
        
        # Find next unanswered question, considering conditional logic
        for question in self.current_template.questions:
            if question.id not in self.responses:
                # Check if this question should be skipped based on conditional logic
                if self._should_skip_question(question):
                    continue
                    
                self.current_question = question
                # Get behavior mode from session state if available
                import streamlit as st
                behavior_mode = getattr(st.session_state, 'behavior_mode', 'casual')
                return self._format_question(question, behavior_mode)
        
        return None  # All questions answered
    
    def _format_question(self, question: Question, behavior_mode: str = "casual") -> str:
        """Format a question for conversational presentation using GPT"""
        try:
            if behavior_mode == "formal":
                style_instructions = """
                Style: Professional and formal
                - Use formal language and complete sentences
                - Address the user professionally 
                - Avoid emojis and casual expressions
                - Use structured, clear formatting
                - Be respectful and courteous
                """
                format_examples = """
                - For 2 options: "Please select: Option1 or Option2"
                - For 3-4 options: "Please choose from: A, B, or C"  
                - For 5+ options: numbered list with "Please select from the following:"
                - For open text: "Please provide your response:"
                """
            else:
                style_instructions = """
                Style: Casual and friendly
                - Make it sound natural and conversational
                - Use emojis sparingly (max 1-2)
                - Avoid repetitive phrases like "quick question" - vary your language
                - Keep it concise but friendly
                """
                format_examples = """
                - For 2 options: "You can answer: **Option1** or **Option2**"
                - For 3-4 options: "You can choose: **A**, **B**, or **C**"  
                - For 5+ options: numbered list
                - For open text: "💬 Please type your answer"
                """
            
            prompt = f"""
            Convert this intake form question into the specified communication style. Only return the final question, no explanations.
            
            Original Question: "{question.question_text}"
            Field Type: {question.field_type}
            Response Options: {question.field_responses if question.field_responses else "Open text"}
            
            {style_instructions}
            
            Instructions:
            1. Change "individual" to "you" for personalization  
            2. If there are response options, present them clearly
            3. ONLY return the formatted question, nothing else
            
            {format_examples}
            """
            
            response = self.client.chat.completions.create(
                model=self.get_selected_model(),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Return ONLY the formatted question, no explanations or meta-commentary."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error formatting question: {e}")
            # Fallback to original question
            return question.question_text
    
    def process_answer(self, user_input: str) -> Tuple[str, bool, Optional[str]]:
        """Process user's answer using GPT for all intelligence"""
        if not self.current_question:
            return "I don't have a current question. Let me get the next one for you.", False, None
        
        # Get behavior mode from session state
        import streamlit as st
        behavior_mode = getattr(st.session_state, 'behavior_mode', 'casual')
        
        # Use GPT to analyze the user's input and determine the appropriate response
        try:
            question_context = {
                "question": self.current_question.question_text,
                "field_type": self.current_question.field_type,
                "response_options": self.current_question.field_responses,
                "user_input": user_input,
                "behavior_mode": behavior_mode
            }
            
            prompt = f"""
            You are a social services intake assistant. Analyze the user's response to determine the appropriate action.
            
            CONTEXT:
            Question: "{self.current_question.question_text}"
            Field Type: {self.current_question.field_type}
            Response Options: {self.current_question.field_responses if self.current_question.field_responses else "Open text"}
            User's Input: "{user_input}"
            Communication Style: {behavior_mode.upper()}
            
            COMMUNICATION STYLE RULES:
            {"FORMAL: Use professional language, complete sentences, avoid emojis, be respectful and structured." if behavior_mode == "formal" else "CASUAL: Use friendly, conversational tone, emojis OK (sparingly), be warm and approachable."}
            
            ANALYSIS TASKS:
            1. Determine if the user is:
               a) AVOIDING the question (e.g., "I don't want to answer", "skip this")
               b) ASKING FOR HELP/EXPLANATION (e.g., "why do you need this?", "what does this mean?")
               c) PROVIDING AN ANSWER (relevant or irrelevant)
            
            2. If AVOIDING: Provide gentle persuasion explaining why the info is needed
            3. If ASKING FOR HELP: Explain why this information is important for social services
            4. If ANSWERING: Check if the answer is appropriate for the question
            
            RESPONSE FORMAT - Return ONLY valid JSON:
            {{
                "action": "avoid|help|answer",
                "is_valid_answer": true/false,
                "response_message": "Your response to the user",
                "should_record": true/false,
                "suggestion": "Additional guidance if needed"
            }}
            
            GUIDELINES:
            - Be empathetic and understanding
            - Explain confidentiality when needed
            - For invalid answers, provide examples of good responses
            - For help requests, explain the purpose clearly
            - For avoidance, gently persuade while respecting boundaries
            - MATCH THE COMMUNICATION STYLE ({behavior_mode.upper()}) in your response_message
            - CRITICAL: Return ONLY valid JSON, no other text
            """
            
            response = self.client.chat.completions.create(
                model=self.get_selected_model(),
                messages=[
                    {"role": "system", "content": "You are an intelligent social services intake assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Parse GPT response
            gpt_response = response.choices[0].message.content.strip()
            print(f"DEBUG: GPT response: {gpt_response}")
            
            try:
                result = json.loads(gpt_response)
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                print(f"Raw response: {gpt_response}")
                # Fallback to simple validation
                return self._simple_fallback_validation(user_input)
            
            # If it's a valid answer, record it and move to next question
            if result.get("should_record", False) and result.get("is_valid_answer", False):
                self.responses[self.current_question.id] = user_input
                self._update_standard_fields(self.current_question, user_input)
                
                # Generate confirmation and get next question
                confirmation = self._generate_confirmation(user_input)
                next_question = self.get_next_question()
                
                if next_question:
                    return f"{confirmation}\n\n{next_question}", True, None
                else:
                    return confirmation, True, None
            else:
                # Return GPT's guidance
                return result.get("response_message", "I need a bit more information."), False, result.get("suggestion")
                
        except Exception as e:
            print(f"GPT analysis error: {e}")
            # Fallback to simple validation
            return self._simple_fallback_validation(user_input)
    
    def _simple_fallback_validation(self, user_input: str) -> Tuple[str, bool, Optional[str]]:
        """Simple fallback if GPT fails"""
        if not user_input.strip():
            return "Please provide an answer to continue.", False, None
        
        # For multiple choice questions, check if answer matches options
        if self.current_question.field_responses:
            user_lower = user_input.lower().strip()
            valid_options = [opt.lower().strip() for opt in self.current_question.field_responses]
            
            if user_lower in valid_options or any(user_lower in opt for opt in valid_options):
                self.responses[self.current_question.id] = user_input
                self._update_standard_fields(self.current_question, user_input)
                
                confirmation = self._generate_confirmation(user_input)
                next_question = self.get_next_question()
                
                if next_question:
                    return f"{confirmation}\n\n{next_question}", True, None
                else:
                    return confirmation, True, None
            else:
                options_text = " • ".join(self.current_question.field_responses)
                return f"Please choose one of these options: {options_text}", False, None
        else:
            # Open text question - accept any non-empty answer
            self.responses[self.current_question.id] = user_input
            self._update_standard_fields(self.current_question, user_input)
            
            confirmation = self._generate_confirmation(user_input)
            next_question = self.get_next_question()
            
            if next_question:
                return f"{confirmation}\n\n{next_question}", True, None
            else:
                return confirmation, True, None
    
    def _should_skip_question(self, question: Question) -> bool:
        """Check if a question should be skipped based on conditional logic"""
        if not question.conditional_logic or not self.responses:
            return False
        
        logic = question.conditional_logic.lower()
        
        # Simple conditional logic based on previous responses
        skip_conditions = {
            "not married": lambda: any("no" in str(resp).lower() for qid, resp in self.responses.items() 
                                    if "married" in self._get_question_text(qid).lower()),
            "no court case": lambda: any("no" in str(resp).lower() for qid, resp in self.responses.items() 
                                       if "court" in self._get_question_text(qid).lower()),
            "no substance": lambda: any("no" in str(resp).lower() for qid, resp in self.responses.items() 
                                      if "substance" in self._get_question_text(qid).lower()),
            "no benefits": lambda: any("no" in str(resp).lower() for qid, resp in self.responses.items() 
                                     if "benefit" in self._get_question_text(qid).lower())
        }
        
        for condition, check_func in skip_conditions.items():
            if condition in logic and check_func():
                return True
        
        return False
    
    def _get_question_text(self, question_id: str) -> str:
        """Get question text by ID"""
        for question in self.current_template.questions:
            if question.id == question_id:
                return question.question_text
        return ""
    
    def _update_standard_fields(self, question: Question, answer: str):
        """Update standard personal/address info based on question content"""
        question_lower = question.question_text.lower()
        
        # Personal info mappings
        if 'first name' in question_lower:
            self.personal_info.person_first_name = answer
        elif 'last name' in question_lower:
            self.personal_info.person_last_name = answer
        elif 'email' in question_lower:
            self.personal_info.person_email_address = answer
        elif 'phone' in question_lower:
            self.personal_info.person_phone_number = answer
        elif 'birth' in question_lower or 'age' in question_lower:
            self.personal_info.person_date_of_birth = answer
        elif 'gender' in question_lower:
            self.personal_info.person_gender = answer
        elif 'race' in question_lower:
            self.personal_info.person_race = answer
        
        # Address info mappings
        elif 'address' in question_lower and 'line 1' in question_lower:
            self.address_info.address_line_1 = answer
        elif 'city' in question_lower:
            self.address_info.address_city = answer
        elif 'state' in question_lower:
            self.address_info.address_state = answer
        elif 'zip' in question_lower or 'postal' in question_lower:
            self.address_info.address_postal_code = answer
    
    def _generate_confirmation(self, answer: str) -> str:
        """Generate a friendly confirmation message"""
        confirmations = [
            f"Got it! I've recorded your answer: {answer}",
            f"Thank you! I've noted: {answer}",
            f"Perfect! I've saved: {answer}",
            f"Excellent! I've recorded: {answer}"
        ]
        
        import random
        return random.choice(confirmations)
    
    def generate_summary(self) -> str:
        """Generate a summary of all responses"""
        if not self.current_template:
            return "No form data available."
        
        summary = f"## Summary of {self.current_template.name}\n\n"
        
        # Add personal info
        if self.personal_info.person_first_name or self.personal_info.person_last_name:
            summary += "**Personal Information:**\n"
            if self.personal_info.person_first_name:
                summary += f"• Name: {self.personal_info.person_first_name}"
                if self.personal_info.person_last_name:
                    summary += f" {self.personal_info.person_last_name}"
                summary += "\n"
            if self.personal_info.person_email_address:
                summary += f"• Email: {self.personal_info.person_email_address}\n"
            if self.personal_info.person_phone_number:
                summary += f"• Phone: {self.personal_info.person_phone_number}\n"
            summary += "\n"
        
        # Add custom responses
        if self.responses:
            summary += "**Your Responses:**\n"
            for question in self.current_template.questions:
                if question.id in self.responses:
                    summary += f"• {question.question_text}: {self.responses[question.id]}\n"
        
        return summary
    
    def create_assistance_request(self) -> AssistanceRequest:
        """Create an AssistanceRequest object from the collected data"""
        if not self.current_template:
            raise ValueError("No template selected")
        
        return AssistanceRequest(
            assistance_request_id=f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=f"Intake form submission for {self.current_template.organization}",
            service_id="intake_001",
            provider_id=self.current_template.organization.lower().replace(" ", "_"),
            case_id=f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            form_id=self.current_template.id,
            personal_info=self.personal_info,
            address_info=self.address_info,
            custom_responses=self.responses,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
