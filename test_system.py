#!/usr/bin/env python3
"""
Test script to verify the chatbot system functionality
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        import openai
        print("✅ OpenAI imported successfully")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        from data_models import DataManager, Question, FormTemplate
        print("✅ Data models imported successfully")
        
        from chatbot_engine import ChatbotEngine
        print("✅ Chatbot engine imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_loading():
    """Test data loading from Excel files"""
    print("\nTesting data loading...")
    try:
        from data_models import DataManager
        dm = DataManager()
        templates = dm.get_all_templates()
        
        if templates:
            print(f"✅ Successfully loaded {len(templates)} templates:")
            for key, template in templates.items():
                print(f"   - {template.organization}: {len(template.questions)} questions")
        else:
            print("⚠️  No templates loaded (this is expected if Excel files are not accessible)")
        
        return True
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_chatbot_engine():
    """Test chatbot engine functionality"""
    print("\nTesting chatbot engine...")
    try:
        from data_models import Question, FormTemplate
        from chatbot_engine import ChatbotEngine
        import uuid
        
        # Create a simple test template
        test_questions = [
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
                question_text="What is your email?",
                field_type="email",
                field_responses=[],
                help_text="We use email to send you updates and resources."
            )
        ]
        
        test_template = FormTemplate(
            id=str(uuid.uuid4()),
            name="Test Template",
            organization="Test Organization",
            description="A simple test template",
            questions=test_questions,
            standard_fields=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        chatbot = ChatbotEngine()
        welcome_msg = chatbot.start_conversation(test_template)
        print("✅ Chatbot engine initialized successfully")
        print(f"   Welcome message: {welcome_msg[:50]}...")
        
        # Test getting next question
        next_question = chatbot.get_next_question()
        if next_question:
            print(f"✅ Next question retrieved: {next_question[:50]}...")
        
        # Test answer processing (without OpenAI call)
        response, is_valid, suggestion = chatbot.process_answer("John Doe")
        print(f"✅ Answer processing works: valid={is_valid}")
        
        return True
    except Exception as e:
        print(f"❌ Chatbot engine error: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI connection...")
    try:
        import openai
        import config
        
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, this is a test. Please respond with 'Test successful'."}],
            max_tokens=10
        )
        
        if response and response.choices:
            print("✅ OpenAI API connection successful")
            print(f"   Response: {response.choices[0].message.content}")
        else:
            print("⚠️  OpenAI API connection issue - no response")
        
        return True
    except Exception as e:
        print(f"❌ OpenAI connection error: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("\nTesting file operations...")
    try:
        # Test output directory creation
        os.makedirs("output", exist_ok=True)
        print("✅ Output directory created/verified")
        
        # Test sample data access
        sample_files = []
        if os.path.exists("Sample Data"):
            sample_files = [f for f in os.listdir("Sample Data") if f.endswith('.xlsx')]
            print(f"✅ Found {len(sample_files)} Excel files in Sample Data")
        else:
            print("⚠️  Sample Data directory not found")
        
        return True
    except Exception as e:
        print(f"❌ File operations error: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 Interactive Intake Chatbot System - Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_file_operations,
        test_data_loading,
        test_chatbot_engine,
        test_openai_connection
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo run the application:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
