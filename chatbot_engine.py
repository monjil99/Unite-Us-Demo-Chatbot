import openai
from typing import Dict, List, Optional, Any, Tuple
import json
import re
from datetime import datetime
from data_models import Question, FormTemplate, AssistanceRequest, PersonalInfo, AddressInfo
import config

class ChatbotEngine:
    """AI-powered chatbot for interactive form filling"""
    
    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.conversation_history = []
        self.current_question = None
        self.current_template = None
        self.responses = {}
        self.personal_info = PersonalInfo()
        self.address_info = AddressInfo()
    
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
                return self._format_question(question)
        
        return None  # All questions answered
    
    def _format_question(self, question: Question) -> str:
        """Format a question for conversational presentation"""
        question_text = self._make_question_conversational(question.question_text)
        
        # Add response options for multiple choice questions in a conversational way
        if question.field_responses and len(question.field_responses) > 0:
            categorical_types = ['dropdown', 'drop down-single select', 'radio', 'single select']
            if question.field_type.lower() in categorical_types:
                if len(question.field_responses) <= 2:
                    # For 2 options, show with "or"
                    options = " or ".join([f"**{opt}**" for opt in question.field_responses])
                    question_text += f"\n\nYou can answer: {options}"
                elif len(question.field_responses) <= 4:
                    # For 3-4 options, show with commas and "or"
                    if len(question.field_responses) == 3:
                        options = f"**{question.field_responses[0]}**, **{question.field_responses[1]}**, or **{question.field_responses[2]}**"
                    else:  # 4 options
                        options = f"**{question.field_responses[0]}**, **{question.field_responses[1]}**, **{question.field_responses[2]}**, or **{question.field_responses[3]}**"
                    question_text += f"\n\nYou can choose: {options}"
                else:
                    # For 5+ options, use a clean numbered list
                    options_list = "\n".join([f"{i+1}. **{opt}**" for i, opt in enumerate(question.field_responses)])
                    question_text += f"\n\nPlease choose from these options:\n{options_list}"
                    
            elif question.field_type.lower() in ['checkbox', 'multi select']:
                if len(question.field_responses) <= 3:
                    # For short lists, show inline with commas
                    options = ", ".join([f"**{opt}**" for opt in question.field_responses])
                    question_text += f"\n\nYou can select: {options} (choose one or more)"
                else:
                    # For longer lists, use numbered format
                    options_list = "\n".join([f"{i+1}. **{opt}**" for i, opt in enumerate(question.field_responses)])
                    question_text += f"\n\nYou can select multiple options from:\n{options_list}"
        
        # Add format hints for specific field types
        format_hints = {
            'email': "💌 Please provide a valid email address (like john@example.com)",
            'phone': "📞 Please provide your phone number (like 555-123-4567)",
            'date': "📅 Please provide the date (like MM/DD/YYYY or January 1, 1990)",
            'number': "🔢 Please provide a number",
            'free text box': "💬 Please type your answer",
            'text': "💬 Please type your answer"
        }
        
        field_type_lower = question.field_type.lower()
        for hint_key, hint_text in format_hints.items():
            if hint_key in field_type_lower:
                question_text += f"\n\n{hint_text}"
                break
        
        return question_text
    
    def _make_question_conversational(self, question_text: str) -> str:
        """Convert formal question text to conversational format"""
        # Handle common patterns and make them more conversational
        conversational_mappings = {
            "Does individual have a court case?": "Do you currently have any ongoing court cases?",
            "Referral source to Court:": "How did you find out about our court services?",
            "City / Ciudad": "What city do you live in?",
            "What is your monthly TANF benefit?": "Do you receive TANF benefits? If yes, what's your monthly amount?",
            "Are you currently participating in any Y programs?": "Are you currently participating in any YMCA programs?",
            "Program Currently Enrolled": "Which program are you currently enrolled in or interested in?",
            "Secondary Contact Information to reach you (Phone Number)": "Is there another phone number we can reach you at?",
            "Secondary Contact Information to reach you (Email)": "Do you have an alternate email address?",
            "Preferred Method of contact (Select all that apply)": "How would you prefer us to contact you?",
            "Preferred Language": "What language would you prefer for our communications?",
            "Other phone or email": "Do you have any other contact information you'd like to share?",
            "Pronouns (optional)": "What pronouns do you use? (This is optional)",
            "Is the individual a Broomfield resident?": "Are you a Broomfield resident?",
            "Does the individual have a history of substance abuse?": "Do you have a history of substance abuse?",
            "What is the individual's drug of choice?": "What is your primary substance of concern?",
            "Does the individual have a family history of substance abuse?": "Does your family have a history of substance abuse?"
        }
        
        # Check for exact matches first
        if question_text in conversational_mappings:
            return conversational_mappings[question_text]
        
        # Handle partial matches and common patterns
        text_lower = question_text.lower()
        
        if "court case" in text_lower:
            return "Do you currently have any ongoing court cases?"
        elif "referral source" in text_lower and "court" in text_lower:
            return "How did you find out about our court services?"
        elif "city" in text_lower or "ciudad" in text_lower:
            return "What city do you live in?"
        elif "tanf" in text_lower:
            return "Do you receive TANF benefits? If yes, what's your monthly amount?"
        elif "y programs" in text_lower or "ymca" in text_lower:
            return "Are you currently participating in any YMCA programs?"
        elif "program" in text_lower and "enrolled" in text_lower:
            return "Which program are you interested in or currently enrolled in?"
        elif "secondary contact" in text_lower and "phone" in text_lower:
            return "Is there another phone number we can reach you at?"
        elif "secondary contact" in text_lower and "email" in text_lower:
            return "Do you have an alternate email address?"
        elif "preferred method" in text_lower and "contact" in text_lower:
            return "How would you prefer us to contact you?"
        elif "preferred language" in text_lower:
            return "What language would you prefer for our communications?"
        elif "pronouns" in text_lower:
            return "What pronouns do you use? (This is optional)"
        elif "other phone or email" in text_lower:
            return "Do you have any other contact information you'd like to share?"
        elif "juvenile or adult" in text_lower or ("juvenile" in text_lower and "adult" in text_lower):
            return "Are you applying as a juvenile (under 18) or as an adult?"
        elif "adult" in text_lower and "juvenile" in text_lower:
            return "Are you applying as a juvenile (under 18) or as an adult?"
        
        # If no specific mapping found, make it more conversational
        # Convert "individual" and "the individual" to "you"
        converted_text = question_text
        converted_text = re.sub(r'\bthe individual\b', 'you', converted_text, flags=re.IGNORECASE)
        converted_text = re.sub(r'\bindividual\b', 'you', converted_text, flags=re.IGNORECASE)
        converted_text = re.sub(r'\bDoes you\b', 'Do you', converted_text, flags=re.IGNORECASE)
        converted_text = re.sub(r'\bIs you\b', 'Are you', converted_text, flags=re.IGNORECASE)
        converted_text = re.sub(r'\bHas you\b', 'Do you have', converted_text, flags=re.IGNORECASE)
        
        if converted_text.endswith("?"):
            return converted_text
        elif converted_text.endswith(":"):
            return converted_text[:-1] + "?"
        else:
            return converted_text + "?"
    
    def _should_skip_question(self, question: Question) -> bool:
        """Check if a question should be skipped based on conditional logic and smart rules"""
        if not question.conditional_logic:
            # Apply smart rules based on question content and previous answers
            return self._apply_smart_skip_rules(question)
        
        # Parse conditional logic
        logic = question.conditional_logic.lower().strip()
        
        # Handle common conditional patterns
        try:
            import re
            
            # Pattern 1: "If Q1 = 'Yes', show this question"
            pattern1 = r'if\s+q?(\d+)\s*=\s*[\'"]?([^\'"]+)[\'"]?'
            match1 = re.search(pattern1, logic)
            
            if match1:
                question_num = int(match1.group(1))
                expected_value = match1.group(2).strip().lower()
                
                # Find the referenced question's answer
                for q in self.current_template.questions:
                    if q.number == question_num and q.id in self.responses:
                        actual_value = self.responses[q.id].lower().strip()
                        # Show only if values match
                        return actual_value != expected_value
                
                # If referenced question not answered yet, skip for now
                return True
            
            # Pattern 2: "Skip if Q2 != 'Married'"
            pattern2 = r'skip\s+if\s+q?(\d+)\s*!=\s*[\'"]?([^\'"]+)[\'"]?'
            match2 = re.search(pattern2, logic)
            
            if match2:
                question_num = int(match2.group(1))
                expected_value = match2.group(2).strip().lower()
                
                # Find the referenced question's answer
                for q in self.current_template.questions:
                    if q.number == question_num and q.id in self.responses:
                        actual_value = self.responses[q.id].lower().strip()
                        # Skip if values don't match
                        return actual_value != expected_value
                
                # If referenced question not answered yet, don't skip
                return False
                
        except (ValueError, AttributeError):
            pass
        
        # Apply smart rules as fallback
        return self._apply_smart_skip_rules(question)
    
    def _apply_smart_skip_rules(self, question: Question) -> bool:
        """Apply smart rules to skip irrelevant questions based on context"""
        question_text = question.question_text.lower()
        
        # Rule 1: Skip court-related follow-up questions if no court case
        if "referral source" in question_text and "court" in question_text:
            # Look for previous court case answer
            for q in self.current_template.questions:
                if "court case" in q.question_text.lower() and q.id in self.responses:
                    answer = self.responses[q.id].lower().strip()
                    if answer in ['no', 'n', 'none', 'not applicable', 'na']:
                        return True  # Skip referral source question
        
        # Rule 2: Skip spouse-related questions if not married
        if "spouse" in question_text or "partner" in question_text:
            for q in self.current_template.questions:
                if "married" in q.question_text.lower() or "marital" in q.question_text.lower():
                    if q.id in self.responses:
                        answer = self.responses[q.id].lower().strip()
                        if answer in ['no', 'single', 'divorced', 'widowed', 'separated']:
                            return True  # Skip spouse questions
        
        # Rule 3: Skip program-specific questions based on program selection
        if "program" in question_text and any(prog in question_text for prog in ['dads', 'moms', 'epic', 'mend']):
            # Look for program enrollment answer
            for q in self.current_template.questions:
                if "program" in q.question_text.lower() and "enrolled" in q.question_text.lower():
                    if q.id in self.responses:
                        answer = self.responses[q.id].lower()
                        # Skip if this specific program wasn't selected
                        if 'dads' in question_text and 'dads' not in answer:
                            return True
                        if 'epic' in question_text and 'epic' not in answer:
                            return True
                        if 'mend' in question_text and 'mend' not in answer:
                            return True
        
        # Rule 4: Skip benefit amount questions if person doesn't receive benefits
        if "benefit" in question_text and ("amount" in question_text or "monthly" in question_text):
            for q in self.current_template.questions:
                if "benefit" in q.question_text.lower() and q.id in self.responses:
                    answer = self.responses[q.id].lower().strip()
                    if answer in ['no', 'none', '0', 'not applicable', 'na', 'do not receive']:
                        return True  # Skip amount questions
        
        # Rule 5: Skip secondary contact if person prefers not to provide
        if "secondary" in question_text or "alternate" in question_text:
            # Check if they indicated they don't want to provide additional contact
            for q in self.current_template.questions:
                if q.id in self.responses:
                    answer = self.responses[q.id].lower().strip()
                    if answer in ['no', 'none', 'not needed', 'no thanks', 'skip']:
                        return True
        
        return False  # Don't skip by default
    
    def process_answer(self, user_input: str) -> Tuple[str, bool, Optional[str]]:
        """
        Process user's answer and return response, validation status, and suggestion
        Returns: (response_message, is_valid, suggestion)
        """
        if not self.current_question:
            return "I don't have a current question. Let me get the next one for you.", False, None
        
        # Check if user is asking for help or expressing confusion
        if self._is_help_request(user_input) or self._is_confusion_expression(user_input):
            return self._generate_intelligent_explanation(user_input), False, None
        
        # Check if user is avoiding the question
        if self._is_avoidance(user_input):
            return self._handle_avoidance(), False, None
        
        # Validate the answer
        is_valid, suggestion = self._validate_answer(user_input, self.current_question)
        
        if is_valid:
            # Store the answer
            self.responses[self.current_question.id] = user_input
            
            # Update personal/address info if applicable
            self._update_standard_fields(self.current_question, user_input)
            
            # Generate confirmation message
            confirmation = self._generate_confirmation(user_input)
            
            # Move to next question
            next_question = self.get_next_question()
            if next_question:
                response = f"{confirmation}\n\n---\n\n{next_question}"
            else:
                response = f"{confirmation}\n\n🎉 **Excellent!** We've completed all the questions. Let me prepare your submission summary."
            
            return response, True, None
        else:
            return f"I need a bit more information. {suggestion}", False, suggestion
    
    def _is_help_request(self, user_input: str) -> bool:
        """Check if user is asking for help about the question"""
        help_patterns = [
            r"why.*need.*this",
            r"why.*ask.*this",
            r"what.*for",
            r"help",
            r"explain",
            r"don't understand",
            r"not sure",
            r"what.*mean",
            r"what does.*mean",
            r"what is.*mean",
            r"what is \w+",  # "what is juvenile"
            r"what does \w+",  # "what does substance"
            r".*what does this mean",
            r".*what is this",
            r"can you explain",
            r"can you share",
            r"tell me about",
            r"how.*used",
            r"what.*happen.*with",
            r"what.*do.*with"
        ]
        
        user_lower = user_input.lower()
        return any(re.search(pattern, user_lower) for pattern in help_patterns)
    
    def _is_avoidance(self, user_input: str) -> bool:
        """Check if user is avoiding answering the question"""
        avoidance_patterns = [
            r"don[''']?t want to answer",
            r"dotn[''']? want to answer",
            r"dont want to answer",
            r"skip this",
            r"pass",
            r"next question",
            r"don[''']?t want to say",
            r"prefer not to",
            r"rather not",
            r"none of your business",
            r"private",
            r"can[''']?t answer"
        ]
        
        user_lower = user_input.lower()
        return any(re.search(pattern, user_lower) for pattern in avoidance_patterns)
    
    def _is_confusion_expression(self, user_input: str) -> bool:
        """Check if user is expressing confusion or asking why"""
        confusion_patterns = [
            r"i don[''']?t get it",
            r"don[''']?t understand",
            r"why.*question",
            r"why.*ask",
            r"confused",
            r"what does this mean",
            r"i don[''']?t know why",
            r"not sure why",
            r"why do you need",
            r"what[''']?s the point"
        ]
        
        user_lower = user_input.lower()
        return any(re.search(pattern, user_lower) for pattern in confusion_patterns)
    
    def _generate_intelligent_explanation(self, user_input: str) -> str:
        """Generate an intelligent explanation using GPT-4o mini"""
        try:
            question_text = self.current_question.question_text
            
            prompt = f"""
            You are a helpful assistant for a social services intake form. A user is confused about this question: "{question_text}"
            
            The user said: "{user_input}"
            
            Please provide a brief, empathetic explanation (2-3 sentences) about:
            1. Why this information is needed for social services
            2. How it helps connect them with appropriate resources
            3. Reassure them about privacy/confidentiality if relevant
            
            Be conversational, friendly, and understanding. Don't repeat the question.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a compassionate social services intake assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            explanation = response.choices[0].message.content.strip()
            return f"{explanation}\n\nWould you like to answer the question now?"
            
        except Exception as e:
            # Fallback explanation
            if not self.current_question:
                return "I understand you have questions. Let me help clarify what we need and why."
            
            question_text = self.current_question.question_text
            fallback_explanations = {
                "drug": "I understand this feels personal. We ask about substance use so we can connect you with the right support services if needed. This information is confidential and helps us provide better care.",
                "substance abuse": "History of substance abuse means past or current problems with drugs or alcohol that have affected your life, work, relationships, or health. We ask this to understand what support services might be helpful for you.",
                "substance": "This helps us understand what kind of support might be helpful. All information is kept private and only used to connect you with appropriate resources.",
                "history": "Family history helps us understand potential risk factors and provide better support. This information is confidential and helps our team serve you better.",
                "court": "Legal information helps us understand any constraints or needs you might have. This ensures we provide appropriate services and support.",
                "find out": "We ask how you heard about us to understand which outreach methods work best and to improve our services. This helps us serve the community better.",
                "services": "Understanding how you found us helps us improve our outreach and ensures we're reaching people who need our help most effectively.",
                "referred": "We ask about referrals to understand what services you've already tried and coordinate your care better.",
                "treatment": "We ask about treatment to understand your care history and avoid duplication of services.",
                "resources": "We want to know what resources you've been offered so we can build on existing support and avoid gaps in care.",
                "juvenile": "Juvenile means under 18 years old. We ask this because different services and legal protections apply to minors versus adults.",
                "adult": "Adult means 18 years old or older. This determines which services and legal frameworks apply to your situation."
            }
            
            # Check for specific term questions first
            user_lower = user_input.lower()
            
            # Handle juvenile/adult questions
            if ("what is juvenile" in user_lower or "what is adult" in user_lower) and "juvenile" in question_text.lower():
                return "Juvenile means under 18 years old. We ask this because different services and legal protections apply to minors versus adults.\n\nWould you like to answer the question now?"
            
            # Handle residence questions  
            if ("who would be considered" in user_lower or "what is.*resident" in user_lower) and "resident" in question_text.lower():
                return "A Broomfield resident is someone who lives within the city limits of Broomfield, Colorado. This determines eligibility for certain local services and programs.\n\nWould you like to answer the question now?"
            
            # Handle substance questions
            if ("substance abuse" in user_lower or "what does this mean" in user_lower) and "substance" in question_text.lower():
                return "History of substance abuse means past or current problems with drugs or alcohol that have affected your life, work, relationships, or health. We ask this to understand what support services might be helpful for you.\n\nWould you like to answer the question now?"
            
            question_lower = question_text.lower()
            for key, explanation in fallback_explanations.items():
                if key in question_lower:
                    return f"{explanation}\n\nWould you like to answer the question now?"
            
            return f"I understand this question might seem unclear. We ask this to better understand your situation and connect you with the most helpful resources. All information is confidential. Would you like to answer the question now?"
    
    def _handle_avoidance(self) -> str:
        """Handle when user avoids answering a question"""
        question_text = self.current_question.question_text
        
        persuasion_messages = [
            f"I understand this question might feel personal. However, answering '{question_text}' helps us provide you with the most appropriate support and resources. Your information is completely confidential and only used to help you better.",
            f"I know some questions can be uncomfortable, but '{question_text}' is important for connecting you with the right services. All your responses are kept private and secure. Would you be willing to share this information?",
            f"This question might seem intrusive, but '{question_text}' helps our team understand your needs better. Everything you share is confidential and helps us serve you more effectively. Could you help us by answering?"
        ]
        
        import random
        message = random.choice(persuasion_messages)
        
        # Add options if it's a multiple choice question
        if self.current_question.field_responses:
            if len(self.current_question.field_responses) <= 4:
                options = " • ".join(self.current_question.field_responses)
                message += f"\n\nYour options are: {options}"
        
        return message
    
    def _validate_answer(self, answer: str, question: Question) -> Tuple[bool, Optional[str]]:
        """Validate user's answer against question requirements"""
        answer = answer.strip()
        
        if not answer:
            return False, "Please provide an answer to continue."
        
        field_type = question.field_type.lower()
        
        # Email validation
        if 'email' in field_type:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, answer):
                return False, "Please provide a valid email address (e.g., john@example.com)"
        
        # Phone validation
        elif 'phone' in field_type or 'phone' in question.question_text.lower():
            phone_pattern = r'[\d\s\-\(\)]{10,}'
            if not re.search(phone_pattern, answer):
                return False, "Please provide a valid phone number with at least 10 digits (e.g., 555-123-4567)"
        
        # Date validation
        elif 'date' in field_type or 'birth' in question.question_text.lower():
            date_patterns = [
                r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',
                r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
                r'[A-Za-z]+ \d{1,2},? \d{4}'
            ]
            if not any(re.search(pattern, answer) for pattern in date_patterns):
                return False, "Please provide a valid date (e.g., 01/15/1990, January 15, 1990, or 1990-01-15)"
        
        # Number validation
        elif 'number' in field_type or '$' in question.question_text:
            if not re.search(r'\d+', answer):
                return False, "Please provide a number (digits only or with dollar sign for money amounts)"
        
        # Multiple choice validation
        elif question.field_responses and len(question.field_responses) > 0:
            categorical_types = ['dropdown', 'drop down-single select', 'radio', 'single select']
            if field_type in categorical_types:
                # Check if answer matches one of the options (case insensitive, flexible matching)
                valid_options = [opt.lower().strip() for opt in question.field_responses]
                answer_lower = answer.lower().strip()
                
                # Exact match first
                if answer_lower in valid_options:
                    return True, None
                
                # Partial match (for cases like "Yes" matching "Yes - option")
                for option in valid_options:
                    if answer_lower in option or option in answer_lower:
                        return True, None
                
                # Special handling for common responses
                if answer_lower in ['y', 'yes', 'yep', 'yeah'] and any('yes' in opt.lower() for opt in valid_options):
                    return True, None
                elif answer_lower in ['n', 'no', 'nope', 'nah'] and any('no' in opt.lower() for opt in valid_options):
                    return True, None
                
                # For Yes/No questions, if answer is completely irrelevant, give special guidance
                if len(question.field_responses) == 2 and all(opt.lower() in ['yes', 'no'] for opt in [r.lower() for r in question.field_responses]):
                    if len(answer.split()) > 3:  # Long irrelevant answer
                        return False, f"This question needs a simple Yes or No answer. Please choose: {' or '.join(question.field_responses)}"
                
                options_text = " • ".join(question.field_responses)
                return False, f"Please choose one of these options: {options_text}"
            
            elif field_type in ['checkbox', 'multi select']:
                # For multi-select, check if at least one option is mentioned
                answer_lower = answer.lower()
                valid_options = [opt.lower() for opt in question.field_responses]
                
                # Check if any valid option is mentioned
                found_options = []
                for opt in question.field_responses:
                    if opt.lower() in answer_lower:
                        found_options.append(opt)
                
                if found_options:
                    return True, None
                
                options_text = " • ".join(question.field_responses)
                return False, f"Please select from these options: {options_text}"
        
        # Debug: print field type and responses to understand the data
        print(f"DEBUG: Field type: '{field_type}', Has responses: {bool(question.field_responses)}, Response count: {len(question.field_responses) if question.field_responses else 0}")
        
        # For descriptive/text answers, use GPT to validate relevance and provide examples
        # Also check questions without specific response options (open-ended)
        # AND validate any answer that's clearly not matching the multiple choice options
        should_validate_with_gpt = (
            field_type in ['text', 'free text box', 'textarea'] or 
            (not question.field_responses or len(question.field_responses) == 0) or
            # If it's a multiple choice but answer doesn't match any option, validate with GPT
            (question.field_responses and len(question.field_responses) > 0 and 
             not any(answer.lower().strip() in opt.lower() for opt in question.field_responses) and
             not any(opt.lower() in answer.lower().strip() for opt in question.field_responses))
        )
        
        if should_validate_with_gpt:
            return self._validate_descriptive_answer(answer, question)
        
        return True, None
    
    def _validate_descriptive_answer(self, answer: str, question: Question) -> Tuple[bool, Optional[str]]:
        """Use GPT to validate descriptive answers and provide examples if needed"""
        try:
            # Debug logging
            print(f"DEBUG: Validating answer '{answer}' for question '{question.question_text}'")
            prompt = f"""
            You are validating a user's response to a social services intake form question. 

            Question: "{question.question_text}"
            User's Response: "{answer}"

            Analyze the user's response and determine:
            1. Is this a QUESTION back to you? (like "how is this used?", "why do you need this?")
            2. Is this an ANSWER that's relevant to the question asked?
            3. Is this an ANSWER but completely unrelated/off-topic?

            Rules:
            - If it's a QUESTION, mark as invalid and explain why the info is needed
            - If it's an ANSWER but irrelevant, mark as invalid and provide a good example
            - If it's a relevant ANSWER, mark as valid

            Respond in this exact format:
            VALID: true/false
            TYPE: question/answer/off-topic
            REASON: Brief explanation if invalid
            EXAMPLE: Good answer example if needed (realistic and short)
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a social services intake form validator. Be helpful but concise."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the response
            lines = result.split('\n')
            is_valid = False
            response_type = ""
            reason = ""
            example = ""
            
            for line in lines:
                if line.startswith('VALID:'):
                    is_valid = 'true' in line.lower()
                elif line.startswith('TYPE:'):
                    response_type = line.replace('TYPE:', '').strip().lower()
                elif line.startswith('REASON:'):
                    reason = line.replace('REASON:', '').strip()
                elif line.startswith('EXAMPLE:'):
                    example = line.replace('EXAMPLE:', '').strip()
            
            if is_valid:
                return True, None
            else:
                if response_type == "question":
                    # User asked a question - provide explanation
                    suggestion = f"I understand you're asking about this. {reason}"
                    if example:
                        suggestion += f"\n\n💡 **To answer this question, try:** {example}"
                else:
                    # Off-topic or irrelevant answer
                    suggestion = f"{reason}"
                    if example:
                        suggestion += f"\n\n💡 **Example of a good answer:** {example}"
                
                return False, suggestion
                
        except Exception as e:
            # If GPT validation fails, accept the answer
            print(f"GPT validation error: {e}")
            return True, None
    
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
        elif 'ethnicity' in question_lower:
            self.personal_info.person_ethnicity = answer
        elif 'marital' in question_lower:
            self.personal_info.person_marital_status = answer
        
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
    
    def create_assistance_request(self, description: str = "Assistance request from chatbot") -> AssistanceRequest:
        """Create an AssistanceRequest object from the collected data"""
        import uuid
        
        return AssistanceRequest(
            assistance_request_id=str(uuid.uuid4()),
            description=description,
            service_id=str(uuid.uuid4()),
            provider_id=str(uuid.uuid4()),
            case_id=str(uuid.uuid4()),
            form_id=self.current_template.id if self.current_template else str(uuid.uuid4()),
            personal_info=self.personal_info,
            address_info=self.address_info,
            custom_responses=self.responses,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def get_faq_answer(self, question_text: str) -> str:
        """Get FAQ answer using OpenAI"""
        try:
            prompt = f"""
            You are a helpful assistant for an intake form system. A user is asking about why certain information is needed in an intake form.

            User question: {question_text}

            Provide a brief, friendly explanation (2-3 sentences) about why this information might be needed for social services, healthcare, or community assistance programs. Focus on how it helps connect them with appropriate resources and services.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant explaining why intake form information is collected."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return "This information helps us better understand your needs and connect you with appropriate resources and services."
