# AI Coaching Assistant: An Interactive Code and Writing Analysis Tool

The AI Coaching Assistant is a Streamlit-based web application that provides intelligent feedback on Python code and written text using AWS Bedrock's Claude AI model. It combines real-time code execution capabilities with AI-powered analysis to help developers write better code and improve their writing.

The application offers two primary features:
- Code Assistant: Analyzes Python code for issues, suggests improvements, and provides real-time code execution in a sandboxed environment
- Writing Assistant: Evaluates text content for clarity, coherence, and style while providing actionable improvement suggestions

## Repository Structure
```
.
├── app.py                  # Main application entry point with Streamlit UI implementation
├── backend/               # Core backend functionality
│   ├── __init__.py       # Package initialization
│   ├── ai_coach.py       # AWS Bedrock Claude integration for AI analysis
│   └── code_sandbox.py   # Secure Python code execution environment
├── requirements.txt       # Project dependencies
└── utils/
    └── helpers.py        # Response formatting utilities
```

## Usage Instructions
### Prerequisites
- Python 3.7 or higher
- AWS account with Bedrock access configured
- Required Python packages:
  - streamlit==1.31.0
  - boto3==1.34.14
  - python-dotenv==1.0.0
  - black==24.1.1
  - pylint==3.0.3

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-coaching-assistant

# Create and activate virtual environment
## MacOS/Linux
python3 -m venv venv
source venv/bin/activate

## Windows
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials
```

### Quick Start
1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Select your desired mode from the sidebar:
   - Code Assistant
   - Writing Assistant

3. For Code Assistant:
```python
# Enter Python code in the text area
def example():
    print("Hello, World!")
    
example()
```
- Click "Analyze Code" for AI feedback
- Click "Run Code" to execute the code

4. For Writing Assistant:
- Enter your text in the provided text area
- Click "Analyze Writing" for detailed feedback

### More Detailed Examples

#### Code Analysis Example
```python
# Input code with potential issues
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total/len(numbers)

result = calculate_average([1,2,3,4,5])
print(result)
```

The AI Coach will analyze:
- Potential division by zero
- Error handling
- Code style and best practices
- Performance considerations

#### Writing Analysis Example
```text
Input: "The impact of artificial intelligence on modern society."

The AI will analyze:
- Thesis strength
- Argument coherence
- Grammar and style
- Suggested improvements
```

### Troubleshooting

Common Issues:
1. AWS Bedrock Connection Issues
   - Error: "Could not connect to AWS Bedrock"
   - Solution: 
     ```bash
     aws configure
     # Enter your AWS credentials
     ```
   - Verify region matches in ai_coach.py

2. Code Execution Timeout
   - Error: "Execution timed out"
   - Solution: Break down complex code into smaller chunks
   - Check for infinite loops

3. Memory Issues
   - Error: "MemoryError"
   - Solution: Limit input size in code_sandbox.py
   - Monitor system resources

Debug Mode:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Data Flow
The application processes user input through AI analysis and code execution pipelines, providing immediate feedback and results.

```ascii
User Input --> [Streamlit UI] --> [AI Coach/Code Sandbox]
                                        |
                                        v
                                [AWS Bedrock API]
                                        |
                                        v
Response Format --> [Helpers] --> [Streamlit Display]
```

Component Interactions:
1. Streamlit UI captures user input (code or text)
2. AI Coach communicates with AWS Bedrock using boto3
3. Code Sandbox executes Python code in isolated environment
4. Helper functions format AI responses for display
5. Results are rendered in the Streamlit UI
6. Error handling occurs at each step with appropriate user feedback
7. All components maintain stateless operation for reliability