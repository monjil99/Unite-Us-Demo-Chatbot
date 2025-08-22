#!/usr/bin/env python3
"""
Demo script to test the chatbot functionality
"""

from data_models import DataManager, Question, FormTemplate
from chatbot_engine import ChatbotEngine
import uuid
from datetime import datetime

def create_demo_template():
    """Create a demo template with branching logic"""
    questions = [
        Question(
            id=str(uuid.uuid4()),
            number=1,
            question_text="What is your name?",
            field_type="text",
            field_responses=[],
            help_text="We need your name to personalize our service."
        ),
        Question(
            id=str(uuid.uuid4()),
            number=2,
            question_text="Are you married?",
            field_type="dropdown",
            field_responses=["Yes", "No", "Prefer not to say"],
            help_text="This helps us understand your family situation."
        ),
        Question(
            id=str(uuid.uuid4()),
            number=3,
            question_text="What is your spouse's name?",
            field_type="text",
            field_responses=[],
            conditional_logic="If Q2 = 'Yes'",
            help_text="We may need to contact your spouse for joint services."
        ),
        Question(
            id=str(uuid.uuid4()),
            number=4,
            question_text="What is your email address?",
            field_type="email",
            field_responses=[],
            help_text="We use email to send you updates and resources."
        ),
        Question(
            id=str(uuid.uuid4()),
            number=5,
            question_text="What type of assistance do you need?",
            field_type="checkbox",
            field_responses=["Housing", "Food", "Healthcare", "Transportation", "Employment"],
            help_text="Select all that apply to help us connect you with the right resources."
        )
    ]
    
    return FormTemplate(
        id=str(uuid.uuid4()),
        name="Demo Intake Form",
        organization="Demo Organization",
        description="A demonstration form with branching logic",
        questions=questions,
        standard_fields=[],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def demo_conversation():
    """Run a demo conversation"""
    print("🤖 Chatbot Demo - Testing Question Flow and Branching Logic")
    print("=" * 60)
    
    # Create demo template
    template = create_demo_template()
    
    # Initialize chatbot
    chatbot = ChatbotEngine()
    
    # Start conversation
    welcome = chatbot.start_conversation(template)
    print(f"🤖 Assistant: {welcome}\n")
    
    # Get first question
    question = chatbot.get_next_question()
    if question:
        print(f"🤖 Assistant: {question}\n")
    else:
        print("❌ No questions found!")
        return
    
    # Simulate user answers
    test_answers = [
        "John Doe",           # Name
        "Yes",                # Married
        "Jane Doe",           # Spouse name (shown because married = Yes)
        "john@example.com",   # Email
        "Housing, Food"       # Assistance types
    ]
    
    for i, answer in enumerate(test_answers):
        print(f"👤 User: {answer}")
        
        response, is_valid, suggestion = chatbot.process_answer(answer)
        
        if is_valid:
            print(f"🤖 Assistant: {response}\n")
        else:
            print(f"❌ Invalid answer: {response}")
            if suggestion:
                print(f"💡 Suggestion: {suggestion}\n")
            break
    
    # Show final summary
    if len(chatbot.responses) == len([q for q in template.questions if not chatbot._should_skip_question(q)]):
        print("🎉 Conversation completed!")
        print("\n📋 Summary:")
        summary = chatbot.generate_summary()
        print(summary)
        
        # Create assistance request
        request = chatbot.create_assistance_request("Demo assistance request")
        print(f"\n✅ Created assistance request: {request.assistance_request_id}")
    
    print("\n" + "=" * 60)
    print("Demo completed!")

if __name__ == "__main__":
    demo_conversation()
