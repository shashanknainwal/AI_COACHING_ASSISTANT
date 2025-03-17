# AI Coaching Assistant: An Interactive Learning and Analysis Tool

The AI Coaching Assistant is a comprehensive Streamlit-based web application that combines intelligent feedback on code and writing with STEM tutoring and adaptive learning capabilities. Powered by AWS Bedrock's Claude AI model, it provides personalized learning experiences across multiple domains.

The application offers four primary features:
- Code Assistant: Analyzes Python code for issues, suggests improvements, and provides real-time code execution in a sandboxed environment
- Writing Assistant: Evaluates text content for clarity, coherence, and style while providing actionable improvement suggestions
- STEM Tutor: Offers interactive tutoring across Mathematics, Physics, Chemistry, and Biology with step-by-step solutions
- Adaptive Learning: Generates personalized questions based on subject, topic, and user performance level

## Repository Structure
```
.
├── app.py                  # Main application entry point with Streamlit UI implementation
├── backend/               # Core backend functionality
│   ├── __init__.py       # Package initialization
│   ├── adaptive_learning.py # Adaptive learning system management
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
   - STEM Tutor
   - Adaptive Learning

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

5. For STEM Tutor:
- Select a subject (Math, Physics, Chemistry, or Biology)
- Choose a specific topic within the subject
- Enter your question
- Receive step-by-step solutions and explanations

6. For Adaptive Learning:
- Select your subject and topic
- Start with beginner-level questions
- Progress through difficulty levels based on performance
- Access hints and explanations when needed

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

#### STEM Tutoring Example
```text
Subject: Physics
Topic: Mechanics
Question: "Calculate the acceleration of a 2kg mass with a force of 10N applied."

The tutor will provide:
- Step-by-step solution using F = ma
- Key concepts about Newton's laws
- Visual force diagrams
- Practice problems for reinforcement
```

#### Adaptive Learning Example
```text
Subject: Mathematics
Topic: Algebra
Level: 1 (Beginner)

- Receive progressively challenging questions
- Get immediate feedback on answers
- Access hints when stuck
- View detailed explanations
- Track progress across difficulty levels
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
The application processes user input through multiple pipelines, providing immediate feedback and adaptive content delivery.

```ascii
User Input --> [Streamlit UI] --> [AI Coach/Code Sandbox/Adaptive Learning]
                                        |
                                        v
                                [AWS Bedrock API]
                                        |
                                        v
Response Format --> [Helpers] --> [Streamlit Display]
```

Component Interactions:
1. Streamlit UI captures user input (code, text, or STEM questions)
2. AI Coach communicates with AWS Bedrock using boto3
3. Code Sandbox executes Python code in isolated environment
4. Adaptive Learning system manages progression and content delivery
5. Helper functions format AI responses for display
6. Results are rendered in the Streamlit UI
7. Error handling occurs at each step with appropriate user feedback
8. All components maintain stateless operation for reliability