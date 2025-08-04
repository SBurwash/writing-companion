# How to Create a React Agent: Step-by-Step Guide

This guide walks you through creating a React agent using LangGraph and LangChain, based on the implementation in this codebase.

## What is a React Agent?

A React agent follows the **ReAct** (Reasoning + Acting) pattern:
- **Reasoning**: The agent thinks about what to do
- **Acting**: The agent uses tools to accomplish tasks
- **Observing**: The agent sees the results and decides next steps

## Prerequisites

- Python 3.11+
- Google API key for Gemini
- Basic understanding of LangChain and LangGraph

## Step 1: Set Up Your Project Structure

```
your-react-agent/
├── pyproject.toml
├── .env
├── main.py
├── workflow.py
├── tools.py
└── logging_config.py
```

## Step 2: Install Dependencies

Create a `pyproject.toml` file:

```toml
[project]
name = "your-react-agent"
version = "0.1.0"
description = "A React agent with custom tools"
requires-python = ">=3.11,<4.0"
dependencies = [
    "langgraph (>=0.2.0,<1.0.0)",
    "langchain (>=0.3.27,<0.4.0)",
    "langchain-google-genai (>=2.1.8,<3.0.0)",
    "langchain-community (>=0.3.27,<0.4.0)",
    "duckduckgo-search (>=8.1.1,<9.0.0)",
    "pillow (>=11.3.0,<12.0.0)",
    "python-dotenv (>=0.9.9,<0.10.0)"
]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

## Step 3: Create Environment Configuration

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

## Step 4: Set Up Logging

Create `logging_config.py`:

```python
import logging
import sys

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/app.log')
        ]
    )
```

## Step 5: Define Your Tools

Create `tools.py` with your custom tools:

```python
import logging
from pathlib import Path
from langchain_core.tools import tool
from langchain_community.agent_toolkits import FileManagementToolkit

logger = logging.getLogger(__name__)

def get_file_management_tools():
    """Get file management tools restricted to a specific directory."""
    project_root = Path.cwd()
    working_dir = project_root / "data"  # Your working directory
    
    # Ensure the directory exists
    working_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Initializing FileManagementToolkit with root_dir: {working_dir}")
    
    # Create toolkit restricted to your directory
    file_toolkit = FileManagementToolkit(root_dir=str(working_dir)).get_tools()
    
    logger.info(f"Loaded {len(file_toolkit)} file management tools")
    return file_toolkit

# Example custom tool
@tool
def custom_calculator(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"
```

## Step 6: Create Your Agent Workflow

Create `workflow.py`:

```python
import logging
from io import BytesIO

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from PIL import Image

from .tools import get_file_management_tools

logger = logging.getLogger(__name__)

# Define your agent's system prompt
SYSTEM_PROMPT = """
You are an AI assistant that can help users with various tasks. You have access to:

🛠️ Available Tools:
- File management (read, write, create files)
- Internet search for real-time information
- Custom calculation tools

You can:
- Answer questions using internet research
- Manage files and documents
- Perform calculations
- Help with data analysis

Always be helpful and explain your reasoning process.
"""

def print_stream(stream):
    """Print streaming responses from the agent."""
    for s in stream:
        message = s["messages"][-1]
        logger.info(f"Message received: {message.content[:200]}...")
        message.pretty_print()

def run_workflow():
    """Initialize and run the React agent."""
    logger.info("Initializing workflow")
    
    # Step 1: Set up tools
    file_toolkit = get_file_management_tools()
    tools = [DuckDuckGoSearchRun(), *file_toolkit]
    logger.info(f"Initialized model and loaded {len(tools)} tools")

    # Step 2: Initialize the language model
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Step 3: Set up configuration
    config = {"configurable": {"thread_id": 1}}
    logger.info(f"Set configuration: {config}")

    # Step 4: Create checkpoint system
    checkpointer = InMemorySaver()

    # Step 5: Create the React agent
    graph = create_react_agent(model, tools=tools, checkpointer=checkpointer)
    logger.info("Created ReAct agent graph")

    # Optional: Visualize the agent graph
    Image.open(BytesIO(graph.get_graph().draw_mermaid_png())).show()

    # Step 6: Start the conversation
    logger.info("Starting conversation with initial prompt")
    inputs = {"messages": [("user", SYSTEM_PROMPT)]}
    print_stream(graph.stream(inputs, config, stream_mode="values"))

    # Step 7: Interactive chat loop
    logger.info("Entering interactive chat loop")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        logger.info(f"Received user input: {user_input[:200]}...")
        inputs = {"messages": [("user", user_input)]}
        print_stream(graph.stream(inputs, config, stream_mode="values"))
```

## Step 7: Create Main Entry Point

Create `main.py`:

```python
import os
from dotenv import load_dotenv
from .logging_config import setup_logging
from .workflow import run_workflow

def main():
    """Main entry point for the React agent."""
    
    # Load environment variables
    load_dotenv()

    # Validate API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable not set. "
            "Please set it in your .env file or environment."
        )

    # Setup logging
    setup_logging()

    # Run the workflow
    run_workflow()

if __name__ == "__main__":
    main()
```

## Step 8: Create CLI Interface (Optional)

Create `cli.py`:

```python
from your_package.main import main

if __name__ == "__main__":
    main()
```

## Step 9: Run Your Agent

1. Install dependencies:
```bash
pip install -e .
```

2. Set your API key in `.env`:
```env
GOOGLE_API_KEY=your_key_here
```

3. Run the agent:
```bash
python cli.py
```

## Key Components Explained

### 1. **Tools**
- **Built-in tools**: DuckDuckGoSearchRun for internet search
- **File management**: FileManagementToolkit for file operations
- **Custom tools**: Define your own using the `@tool` decorator

### 2. **Language Model**
- Uses Google's Gemini 2.0 Flash model
- Handles reasoning and decision-making

### 3. **Checkpointer**
- `InMemorySaver` maintains conversation state
- Enables multi-turn conversations

### 4. **Agent Graph**
- `create_react_agent` creates the ReAct workflow
- Handles the reasoning → acting → observing cycle

## Customization Options

### Adding Custom Tools

```python
@tool
def my_custom_tool(input_param: str) -> str:
    """Description of what this tool does."""
    # Your tool logic here
    return "Tool result"
```

### Modifying the System Prompt

Update the `SYSTEM_PROMPT` in `workflow.py` to match your use case:

```python
SYSTEM_PROMPT = """
You are a specialized assistant for [your domain].
Your capabilities include:
- [Capability 1]
- [Capability 2]
- [Capability 3]

Guidelines:
- [Guideline 1]
- [Guideline 2]
"""
```

### Adding More Tools

```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Add Wikipedia tool
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
tools = [DuckDuckGoSearchRun(), wikipedia, *file_toolkit]
```

## Best Practices

1. **Error Handling**: Always wrap tool calls in try-catch blocks
2. **Logging**: Use structured logging for debugging
3. **Tool Descriptions**: Write clear, detailed tool descriptions
4. **State Management**: Use checkpoints for conversation persistence
5. **Security**: Validate inputs and restrict file access appropriately

## Troubleshooting

### Common Issues:

1. **API Key Error**: Ensure `GOOGLE_API_KEY` is set in `.env`
2. **Import Errors**: Check all dependencies are installed
3. **Tool Errors**: Verify tool permissions and file paths
4. **Memory Issues**: Consider using persistent storage for large conversations

This guide provides a complete foundation for building React agents with LangGraph and LangChain. The modular structure allows for easy customization and extension based on your specific needs. 