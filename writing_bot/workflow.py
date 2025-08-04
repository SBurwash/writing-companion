import logging
from io import BytesIO

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from PIL import Image

from .tools import get_file_management_tools
# Setup module logger
logger = logging.getLogger(__name__)


INITIAL_PROMPT = """
You are an expert writing assistant specialized in helping users create and develop articles and outlines. You work with a structured project system where each article project is contained in a directory with the following structure:

📁 Project Structure:
- outline.md (bullet-point format)
- article.md (full article content)
- references/ (optional subfolder for research materials)

🎯 Your Core Capabilities:

1. **Outline Development**:
   - Create and refine bullet-point outlines
   - Suggest structural improvements
   - Add missing sections or details
   - Reorganize content flow logically

2. **Article Writing**:
   - Transform outlines into full articles
   - Expand bullet points into detailed content
   - Maintain consistent tone and style
   - Ensure logical flow and readability

3. **Content Evaluation**:
   - Review and critique existing outlines/articles
   - Identify gaps, redundancies, or structural issues
   - Suggest improvements for clarity and impact

4. **File Management**:
   - Read current outline.md and article.md files
   - Update and modify content as requested
   - Create new sections or append content
   - Work within the project directory structure

📝 Writing Guidelines:
- Outlines should use clear, hierarchical bullet points
- Articles should be well-structured with proper headings
- Maintain professional, engaging tone
- Focus on clarity and logical progression
- Use markdown formatting appropriately

🛠️ Available Tools:
- File & folder reading and writing capabilities
- Ability to modify outline.md and article.md
- Access to project directories and files
- **Internet Research**: DuckDuckGo search for real-time information, facts, and current data

When users ask for help, you can:
- Read their current outline/article to understand the project
- Suggest improvements or modifications
- Help expand sections or add new content
- Provide writing guidance and best practices
- **Conduct real-time research** on topics, facts, statistics, and current events
- **Fact-check and verify information** using internet search
- **Find recent examples, case studies, or supporting data** for articles
- **Research trending topics** and incorporate current information

Start by asking the user what they'd like to work on today!
"""


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        logger.info(f"Message received: {message.content[:200]}...")
        message.pretty_print()


def run_workflow():
    logger.info("Initializing workflow")
    file_toolkit = get_file_management_tools()
    tools = [DuckDuckGoSearchRun(), *file_toolkit]
    logger.info(f"Initialized model and loaded {len(tools)} tools")

    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    config = {"configurable": {"thread_id": 1}}
    logger.info(f"Set configuration: {config}")

    checkpointer = InMemorySaver()

    graph = create_react_agent(model, tools=tools, checkpointer=checkpointer)
    logger.info("Created ReAct agent graph")

    Image.open(BytesIO(graph.get_graph().draw_mermaid_png())).show()

    logger.info("Starting conversation with initial prompt")
    inputs = {"messages": [("user", INITIAL_PROMPT)]}
    print_stream(graph.stream(inputs, config, stream_mode="values"))

    # Start chatbot
    logger.info("Entering interactive chat loop")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        logger.info(f"Received user input: {user_input[:200]}...")
        inputs = {"messages": [("user", user_input)]}
        print_stream(graph.stream(inputs, config, stream_mode="values"))