# 🤖 Interactive Intake Chatbot System

An AI-powered chatbot system that transforms traditional static intake forms into engaging, conversational experiences using GPT-4o mini.

## 🌟 Live Demo

🚀 **[Try the Live Demo on Streamlit Cloud](https://unite-us-demo-chatbot.streamlit.app)** *(Coming Soon)*

## 📋 Overview

This system replaces boring static intake forms with an intelligent, conversational chatbot that:
- **Guides users** through intake questions naturally
- **Validates responses** intelligently using AI
- **Provides help** when users are confused
- **Handles avoidance** with gentle persuasion
- **Adapts communication style** (formal vs. casual)

## ✨ Key Features

### 🧠 **AI-Powered Intelligence**
- **GPT-4o mini** for natural language processing
- **Smart validation** of user responses
- **Context-aware help** and explanations
- **Avoidance detection** and gentle persuasion

### 🎭 **Dual Communication Modes**
- **😊 Casual Mode**: Friendly, conversational with emojis
- **🎩 Formal Mode**: Professional, structured communication
- **Real-time switching** between modes

### 🏢 **Multi-Organization Support**
- **4 Sample Organizations** with real intake forms
- **Role-based authentication** (Admin/Client)
- **Organization-specific** form templates and data

### 📊 **Comprehensive Admin Portal**
- **Form template management** with versioning
- **Application viewing** and analytics
- **Export capabilities** (CSV/JSON)
- **Version control** for form templates

### 🔒 **Security & Privacy**
- **Secure authentication** system
- **Organization data isolation**
- **API key encryption** via Streamlit secrets
- **Session-based** access control

## 🎯 Sample Organizations

| Organization | Username | Password | Focus Area |
|-------------|----------|----------|------------|
| **Broomfield Department of Health** | `broomfield_admin` | `123456` | Court services, substance abuse |
| **First Things First** | `ftf_admin` | `123456` | Early childhood development |
| **Gateway YMCA** | `gateway_admin` | `123456` | Community programs, fitness |
| **SBNJ Mobile Midwife Clinic** | `sbnj_admin` | `123456` | Maternal health services |

## 🚀 Quick Start

### **Option 1: Try the Live Demo**
Visit the deployed application and test with sample credentials above.

### **Option 2: Run Locally**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/monjil99/Unite-Us-Demo-Chatbot.git
   cd Unite-Us-Demo-Chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**: http://localhost:8501

## 🎪 How to Test

### **Client Experience:**
1. **Login as Client** with any organization
2. **Select form template** to begin intake
3. **Try different scenarios**:
   - Valid answers
   - "I don't want to answer"
   - "What does this mean?"
   - Invalid/irrelevant responses
4. **Toggle communication style** (Casual ↔ Formal)
5. **Submit application**

### **Admin Experience:**
1. **Login as Admin** for same organization
2. **View submitted applications** 
3. **Test form management**:
   - Create new templates
   - Edit existing forms (creates versions)
   - Activate different versions
4. **Export data** (CSV/JSON)

## 📁 Project Structure

```
├── app.py                     # Main Streamlit application
├── auth.py                    # Authentication system
├── chatbot_engine_new.py      # GPT-powered chatbot logic
├── client_interface.py        # Client-facing UI
├── admin_interface.py         # Admin portal UI
├── data_models.py            # Data structures and management
├── config.py                 # Configuration and secrets
├── requirements.txt          # Python dependencies
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml          # Secrets template
├── Sample Data/              # Sample intake forms (Excel)
└── output/                   # Generated files and exports
```

## 🔧 Technical Architecture

### **Frontend**
- **Streamlit** for web interface
- **Responsive design** with custom CSS
- **Real-time updates** via session state

### **Backend**
- **Python** with pandas for data processing
- **OpenAI GPT-4o mini** for AI intelligence
- **JSON/Excel** for data persistence

### **AI Integration**
- **Intelligent question formatting**
- **Response validation and guidance**
- **Context-aware help system**
- **Multi-modal communication styles**

## 📊 Sample Intake Forms

The system includes real-world intake forms from:

- **Healthcare services** (substance abuse, mental health)
- **Community programs** (YMCA, youth services)
- **Government services** (court systems, social services)
- **Specialized clinics** (maternal health, mobile services)

## 🛡️ Security Features

- ✅ **API key encryption** via Streamlit secrets
- ✅ **Organization-based access control**
- ✅ **Session management** and authentication
- ✅ **Data isolation** between organizations
- ✅ **Secure file handling** and exports

## 🚀 Deployment

### **Streamlit Cloud Deployment**

1. **Fork this repository** on GitHub
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Create new app** with this repository
4. **Add secrets**:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key-here"
   ```
5. **Deploy!**

### **Environment Variables**

For local development, create a `.env` file:
```env
OPENAI_API_KEY=your-openai-api-key-here
```

## 📈 Future Enhancements

- [ ] **Database integration** (PostgreSQL/MongoDB)
- [ ] **Advanced analytics** and reporting
- [ ] **Multi-language support**
- [ ] **Voice interface** integration
- [ ] **Mobile app** development
- [ ] **API endpoints** for external integration

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

Built for **Unite Us** to demonstrate the future of intake form experiences.

## 📞 Support

For questions or support:
- **Create an issue** on GitHub
- **Check the documentation** in `/docs`
- **Review sample data** in `/Sample Data`

---

🎉 **Transform your intake forms from boring to brilliant!** 🚀