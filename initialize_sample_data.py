#!/usr/bin/env python3
"""
Initialize sample data for the Interactive Intake Chatbot System
This script creates the sample Excel files and initial templates needed for the system to work.
"""

import os
import pandas as pd
from datetime import datetime
import json

def create_sample_excel_files():
    """Create sample Excel files for the intake forms"""
    
    # Ensure Sample Data directory exists
    os.makedirs("Sample Data", exist_ok=True)
    
    # Sample data for Broomfield Department of Health
    broomfield_data = {
        'Question Number': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        'Question': [
            'Do you currently have a court case?',
            'How did you find out about our court services?',
            'Juvenile or Adult?',
            'Are you a Broomfield resident?',
            'Do you have a history of substance abuse?',
            'What is your drug of choice?',
            'Do you have a family history of substance abuse?',
            'Do you need mental health treatment?',
            'Where would you like to receive mental health treatment?',
            'Do you need substance abuse treatment?',
            'Were you referred to substance abuse treatment?',
            'What resources are available to you?',
            'Additional comments'
        ],
        'Field Type': [
            'radio', 'drop down-multi-select', 'radio', 'radio', 'radio',
            'drop down-multi-select', 'radio', 'radio', 'text', 'radio',
            'radio', 'text', 'textarea'
        ],
        'Response Options': [
            'Yes,No',
            'Court Case,Police,Walk In,Phone,Website,Word of Mouth,Other',
            'Juvenile,Adult',
            'Yes,No',
            'Yes,No',
            'Marijuana,Methamphetamine,Cocaine,Opioids (including pills, heroin, and/or fentanyl),Hallucinogens,Barbiturates,Other',
            'Yes,No',
            'Yes,No',
            '',
            'Yes,No',
            'Yes,No',
            '',
            ''
        ]
    }
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(broomfield_data)
    df.to_excel("Sample Data/Broomfield Department of Health ARF - no PII.xlsx", index=False)
    
    # Sample data for Gateway YMCA
    gateway_data = {
        'Question Number': [1, 2, 3, 4, 5, 6, 7, 8],
        'Question': [
            'What is your name?',
            'What is your age?',
            'What services are you interested in?',
            'Do you have transportation?',
            'Emergency contact name',
            'Emergency contact phone',
            'Any medical conditions?',
            'Additional information'
        ],
        'Field Type': [
            'text', 'text', 'drop down-multi-select', 'radio',
            'text', 'text', 'textarea', 'textarea'
        ],
        'Response Options': [
            '',
            '',
            'Youth Programs,Adult Fitness,Swimming,Childcare,Senior Programs,Other',
            'Yes,No',
            '',
            '',
            '',
            ''
        ]
    }
    
    df_gateway = pd.DataFrame(gateway_data)
    df_gateway.to_excel("Sample Data/Gateway YMCA ARF - no PII.xlsx", index=False)
    
    print("✅ Sample Excel files created successfully!")

def create_initial_templates():
    """Create initial form templates"""
    from data_models import DataManager
    
    data_manager = DataManager()
    
    # Initialize with sample data if no templates exist
    if not data_manager.templates:
        print("🔄 Loading sample templates from Excel files...")
        data_manager.load_sample_data()
        print("✅ Sample templates loaded successfully!")
    else:
        print("ℹ️ Templates already exist, skipping initialization.")

def main():
    """Main initialization function"""
    print("🚀 Initializing Interactive Intake Chatbot System...")
    print("=" * 50)
    
    # Create sample Excel files
    create_sample_excel_files()
    
    # Create initial templates
    try:
        create_initial_templates()
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize templates: {e}")
        print("   Templates will be created when the app first runs.")
    
    print("=" * 50)
    print("✅ Initialization complete!")
    print("\n📝 Next steps:")
    print("1. Deploy to Streamlit Cloud")
    print("2. Add your OpenAI API key to secrets")
    print("3. Test the application")

if __name__ == "__main__":
    main()
