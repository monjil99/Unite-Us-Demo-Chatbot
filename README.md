# Interactive Intake Chatbot System

## Installation Guide

### Local Installation

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

### Streamlit Cloud Deployment

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Create new app** with this repository
3. **Add secrets**:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key-here"
   ```
4. **Deploy!**

### Test Credentials

| Organization | Username | Password |
|-------------|----------|----------|
| Broomfield Department of Health | `broomfield_admin` | `123456` |
| First Things First | `ftf_admin` | `123456` |
| Gateway YMCA | `gateway_admin` | `123456` |
| SBNJ Mobile Midwife Clinic | `sbnj_admin` | `123456` |