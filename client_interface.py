import streamlit as st
from datetime import datetime
import os
from data_models import DataManager
from chatbot_engine_new import ChatbotEngine
import json
from auth import is_authenticated, get_user_templates, get_user_info, show_user_header

def show_client_interface():
    """Client interface for interactive chatbot conversation"""
    st.title("💬 Interactive Intake Assistant")
    
    # Show user header with logout option
    show_user_header()
    
    user_info = get_user_info()
    st.markdown(f"Welcome to **{user_info['business_name']}** intake portal!")
    
    # Add behavior mode toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🎭 Chatbot Personality")
        behavior_mode = st.toggle(
            "**Formal Communication Style**",
            value=False,
            help="Toggle between casual/friendly (OFF) and formal/professional (ON) communication style"
        )
        
        if behavior_mode:
            st.info("🎩 **Formal Mode:** Professional, structured communication")
            st.markdown("I'm here to assist you with completing your intake form in a professional manner.")
        else:
            st.info("😊 **Casual Mode:** Friendly, conversational communication")
            st.markdown("I'm here to help you complete your intake form in a friendly, conversational way!")
    
    # Store behavior mode in session state
    st.session_state.behavior_mode = "formal" if behavior_mode else "casual"
    
    # Initialize components
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = ChatbotEngine()
    
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    data_manager = st.session_state.data_manager
    chatbot = st.session_state.chatbot
    
    # Organization selection (if conversation not started)
    if not st.session_state.conversation_started:
        show_organization_selection(data_manager, chatbot)
    else:
        show_chat_interface(chatbot, data_manager)

def show_organization_selection(data_manager, chatbot):
    """Show available form templates for current user"""
    st.header("📋 Available Intake Forms")
    st.write("Please select the form you'd like to complete:")
    
    # Get user's accessible templates
    user_templates = get_user_templates()
    all_templates = data_manager.get_all_templates()
    accessible_templates = {k: v for k, v in all_templates.items() if k in user_templates}
    
    if not accessible_templates:
        user_info = get_user_info()
        st.error(f"No intake forms are currently available for {user_info['business_name']}. Please contact the administrator.")
        return
    
    # Create form cards
    cols = st.columns(2)
    for i, (key, template) in enumerate(accessible_templates.items()):
        with cols[i % 2]:
            with st.container():
                st.subheader(template.organization)
                st.write(f"**Form:** {template.name}")
                st.write(f"**Questions:** {len(template.questions)} questions")
                st.write(f"**Description:** {template.description}")
                
                if st.button(f"Start with {template.organization}", key=f"select_{key}", use_container_width=True):
                    # Start conversation
                    welcome_message = chatbot.start_conversation(template)
                    st.session_state.messages = [{"role": "assistant", "content": welcome_message}]
                    
                    # Immediately ask the first question
                    first_question = chatbot.get_next_question()
                    if first_question:
                        st.session_state.messages.append({"role": "assistant", "content": first_question})
                    
                    st.session_state.conversation_started = True
                    st.session_state.selected_template = key
                    st.rerun()
                
                st.markdown("---")

def show_chat_interface(chatbot, data_manager):
    """Show the main chat interface"""
    
    # Sidebar with progress and help
    with st.sidebar:
        show_sidebar_info(chatbot)
    
    # Main chat area
    st.header("💬 Intake Conversation")
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Check if all questions are answered
    if chatbot.current_template and len(chatbot.responses) >= len(chatbot.current_template.questions):
        show_completion_interface(chatbot, data_manager)
        return
    
    # Show interactive input options for current question
    show_interactive_input(chatbot)
    
    # Chat input for text responses
    if prompt := st.chat_input("Type your answer here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Process the answer
        response, is_valid, suggestion = chatbot.process_answer(prompt)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Show suggestion if answer was invalid
        if not is_valid and suggestion:
            suggestion_msg = f"💡 **Suggestion:** {suggestion}"
            st.session_state.messages.append({"role": "assistant", "content": suggestion_msg})
        
        st.rerun()
    
    # Quick action buttons
    show_quick_actions(chatbot)

def show_interactive_input(chatbot):
    """Show radio buttons or other interactive inputs for categorical questions"""
    if not chatbot.current_template:
        return
    
    # Get the current question
    current_question = None
    for question in chatbot.current_template.questions:
        if question.id not in chatbot.responses and not chatbot._should_skip_question(question):
            current_question = question
            break
    
    if not current_question:
        return
    
    # Check if this is a categorical question that should have radio buttons
    categorical_types = ['dropdown', 'drop down-single select', 'radio', 'single select', 'multi select']
    
    # Debug information
    field_type = current_question.field_type.lower()
    has_responses = current_question.field_responses and len(current_question.field_responses) > 0
    
    if (has_responses and field_type in categorical_types):
        # Only show radio buttons if there are 5 or fewer options
        if len(current_question.field_responses) <= 5:
            st.markdown("### 🔘 Quick Select Options:")
            
            # Create columns for radio buttons
            cols = st.columns(min(len(current_question.field_responses), 3))
            
            for i, option in enumerate(current_question.field_responses):
                with cols[i % 3]:
                    if st.button(f"📍 {option}", key=f"radio_{current_question.id}_{i}", use_container_width=True):
                        # Add user message to chat
                        st.session_state.messages.append({"role": "user", "content": option})
                        
                        # Process the answer
                        response, is_valid, suggestion = chatbot.process_answer(option)
                        
                        # Add assistant response
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        st.rerun()
            
            st.markdown("---")
            st.markdown("*Or type your answer below:*")

def show_sidebar_info(chatbot):
    """Show sidebar with progress and help information"""
    st.title("📊 Progress")
    
    if chatbot.current_template:
        # Calculate actual questions to be asked (considering skip logic)
        total_questions = len(chatbot.current_template.questions)
        answered = len(chatbot.responses)
        
        # Estimate how many questions will be skipped
        estimated_skipped = 0
        for question in chatbot.current_template.questions:
            if question.id not in chatbot.responses and chatbot._should_skip_question(question):
                estimated_skipped += 1
        
        estimated_total = total_questions - estimated_skipped
        progress = answered / estimated_total if estimated_total > 0 else 0
        
        # Ensure progress doesn't exceed 100%
        progress = min(progress, 1.0)
        
        # Create a colored progress bar
        if progress < 0.33:
            progress_color = "🔴"
        elif progress < 0.66:
            progress_color = "🟡"
        else:
            progress_color = "🟢"
        
        st.progress(progress)
        st.write(f"{progress_color} **{answered} of ~{estimated_total} questions completed**")
        st.write(f"**Progress:** {progress:.0%}")
        
        # Show current question number
        if chatbot.current_question:
            current_q_num = next((i+1 for i, q in enumerate(chatbot.current_template.questions) if q.id == chatbot.current_question.id), 0)
            st.write(f"**Current Question:** #{current_q_num}")
    
    st.markdown("---")
    
    # Help section
    st.title("❓ Need Help?")
    st.write("You can ask me:")
    st.write("• *'Why do you need this information?'*")
    st.write("• *'Can you explain this question?'*")
    st.write("• *'What's a good example answer?'*")
    
    st.markdown("---")
    
    # FAQ section
    st.title("📚 Common Questions")
    
    faq_items = [
        ("Why do you ask for my phone number?", "We need your contact information to reach you about services and appointments that match your needs."),
        ("Is my information secure?", "Yes, all information is kept confidential and used only to connect you with appropriate resources."),
        ("How long does this take?", "Most forms take 5-10 minutes to complete, depending on your specific needs."),
        ("Can I come back later?", "Currently, you'll need to complete the form in one session. We're working on a save feature!"),
    ]
    
    for question, answer in faq_items:
        with st.expander(question):
            st.write(answer)


def show_quick_actions(chatbot):
    """Show quick action buttons"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤔 Why is this needed?", use_container_width=True):
            if chatbot.current_question:
                help_text = chatbot.current_question.help_text or "This information helps us provide better assistance."
                st.session_state.messages.append({"role": "user", "content": "Why is this information needed?"})
                st.session_state.messages.append({"role": "assistant", "content": help_text})
                st.rerun()
    
    with col2:
        if st.button("📝 Show my answers", use_container_width=True):
            summary = chatbot.generate_summary()
            st.session_state.messages.append({"role": "user", "content": "Can you show me my answers so far?"})
            st.session_state.messages.append({"role": "assistant", "content": summary})
            st.rerun()
    
    with col3:
        if st.button("🔄 Start over", use_container_width=True):
            st.session_state.conversation_started = False
            st.session_state.messages = []
            st.session_state.chatbot = ChatbotEngine()
            if 'selected_template' in st.session_state:
                del st.session_state.selected_template
            st.rerun()

def show_completion_interface(chatbot, data_manager):
    """Show completion interface when all questions are answered"""
    st.success("🎉 Congratulations! You've completed all the questions!")
    
    # Show summary
    st.header("📋 Your Submission Summary")
    summary = chatbot.generate_summary()
    st.markdown(summary)
    
    # Submission options
    st.header("📤 Submit Your Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Submit Application", type="primary", use_container_width=True):
            submit_application(chatbot, data_manager)
    
    with col2:
        if st.button("📊 Download My Data", use_container_width=True):
            download_data(chatbot)

def submit_application(chatbot, data_manager):
    """Submit the completed application"""
    try:
        # Create assistance request
        description = "Intake form submission via interactive chatbot"
        assistance_request = chatbot.create_assistance_request()
        
        # Generate filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        org_name = chatbot.current_template.organization.replace(" ", "_").lower()
        
        excel_file = f"output/submission_{org_name}_{timestamp}.xlsx"
        json_file = f"output/submission_{org_name}_{timestamp}.json"
        chat_history_file = f"output/chat_history_{org_name}_{timestamp}.json"
        
        # Save to both formats
        data_manager.save_response_to_excel(assistance_request, excel_file)
        data_manager.save_response_to_json(assistance_request, json_file)
        
        # Save chat history
        save_chat_history(chat_history_file, chatbot, assistance_request)
        
        # Save submitted application for admin viewing
        data_manager.save_submitted_application(assistance_request)
        
        st.success(f"""
        ✅ **Application Submitted Successfully!**
        
        **Submission ID:** {assistance_request.assistance_request_id}
        **Submitted:** {assistance_request.created_at.strftime("%Y-%m-%d %H:%M:%S")}
        
        Your information has been saved and will be reviewed by our team. 
        You should hear back within 2-3 business days.
        
        **Files saved:**
        • Excel format: `{excel_file}`
        • JSON format: `{json_file}`
        • Chat history: `{chat_history_file}`
        """)
        
        # Provide download links
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if os.path.exists(excel_file):
                with open(excel_file, 'rb') as f:
                    st.download_button(
                        label="📊 Download Excel File",
                        data=f.read(),
                        file_name=os.path.basename(excel_file),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        
        with col2:
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    st.download_button(
                        label="📄 Download JSON File",
                        data=f.read(),
                        file_name=os.path.basename(json_file),
                        mime="application/json",
                        use_container_width=True
                    )
        
        with col3:
            if os.path.exists(chat_history_file):
                with open(chat_history_file, 'r') as f:
                    st.download_button(
                        label="💬 Download Chat History",
                        data=f.read(),
                        file_name=os.path.basename(chat_history_file),
                        mime="application/json",
                        use_container_width=True
                    )
        
        # Option to start a new application
        if st.button("🆕 Start New Application", type="primary", use_container_width=True):
            st.session_state.conversation_started = False
            st.session_state.messages = []
            st.session_state.chatbot = ChatbotEngine()
            st.rerun()
            
    except Exception as e:
        st.error(f"Error submitting application: {e}")
        st.write("Please try again or contact support if the problem persists.")

def save_chat_history(filename, chatbot, assistance_request):
    """Save the complete chat history in JSON format"""
    try:
        import json
        from datetime import datetime
        
        # Create comprehensive chat history
        chat_history = {
            "submission_info": {
                "submission_id": assistance_request.assistance_request_id,
                "organization": chatbot.current_template.organization,
                "form_name": chatbot.current_template.name,
                "submitted_at": assistance_request.created_at.isoformat(),
                "total_questions": len(chatbot.current_template.questions),
                "questions_answered": len(chatbot.responses)
            },
            "conversation_flow": [],
            "final_responses": {},
            "user_interactions": {
                "help_requests": 0,
                "confusion_expressions": 0,
                "validation_errors": 0
            }
        }
        
        # Process chat messages
        for i, message in enumerate(st.session_state.messages):
            chat_entry = {
                "message_id": i + 1,
                "timestamp": datetime.now().isoformat(),
                "role": message["role"],
                "content": message["content"],
                "message_type": "system" if message["role"] == "assistant" and any(keyword in message["content"].lower() for keyword in ["welcome", "let's get started"]) else "question" if message["role"] == "assistant" else "answer"
            }
            
            # Analyze user interactions
            if message["role"] == "user":
                content_lower = message["content"].lower()
                if any(pattern in content_lower for pattern in ["why", "help", "explain", "don't understand"]):
                    chat_history["user_interactions"]["help_requests"] += 1
                if any(pattern in content_lower for pattern in ["don't get it", "confused", "what does this mean"]):
                    chat_history["user_interactions"]["confusion_expressions"] += 1
            
            if message["role"] == "assistant" and "suggestion" in message["content"].lower():
                chat_history["user_interactions"]["validation_errors"] += 1
            
            chat_history["conversation_flow"].append(chat_entry)
        
        # Add final responses mapping
        for question in chatbot.current_template.questions:
            if question.id in chatbot.responses:
                chat_history["final_responses"][question.question_text] = {
                    "question_id": question.id,
                    "question_type": question.field_type,
                    "user_answer": chatbot.responses[question.id],
                    "question_number": question.number
                }
        
        # Add analytics
        chat_history["analytics"] = {
            "completion_rate": len(chatbot.responses) / len(chatbot.current_template.questions) if chatbot.current_template.questions else 0,
            "total_messages": len(st.session_state.messages),
            "user_messages": len([m for m in st.session_state.messages if m["role"] == "user"]),
            "assistant_messages": len([m for m in st.session_state.messages if m["role"] == "assistant"]),
            "average_response_length": sum(len(m["content"]) for m in st.session_state.messages if m["role"] == "user") / max(1, len([m for m in st.session_state.messages if m["role"] == "user"]))
        }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, indent=2, ensure_ascii=False)
        
        print(f"Chat history saved to {filename}")
        
    except Exception as e:
        print(f"Error saving chat history: {e}")

def download_data(chatbot):
    """Allow user to download their data"""
    try:
        # Create assistance request for download
        assistance_request = chatbot.create_assistance_request()
        
        # Convert to JSON for download
        import json
        from dataclasses import asdict
        
        data_dict = asdict(assistance_request)
        data_dict['created_at'] = assistance_request.created_at.isoformat()
        data_dict['updated_at'] = assistance_request.updated_at.isoformat()
        
        json_data = json.dumps(data_dict, indent=2)
        
        st.download_button(
            label="📥 Download My Data (JSON)",
            data=json_data,
            file_name=f"my_intake_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        st.info("Your data has been prepared for download. This file contains all your responses in JSON format.")
        
    except Exception as e:
        st.error(f"Error preparing download: {e}")

if __name__ == "__main__":
    show_client_interface()
