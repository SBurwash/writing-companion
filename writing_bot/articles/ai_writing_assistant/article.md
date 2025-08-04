# Building a React AI Agent: A Practical Guide for Developers

When the Rubik's Cube rose to fame in the early 1980s, it took the world by storm, selling around [200 million units](https://en.wikipedia.org/wiki/Rubik%27s_Cube) worldwide between 1980 and 1983, and this despite the fact that **most people could only solve a side or 2**.

Somehow, I feel the same way about this latest AI wave - everyone's talking about it, but no one actually knows how to do it.

Thing is, though - my job as a consultant sort of dictates that I need to know things others haven't looked into yet. If you want to give advice, before sharing, you have to have something to give.
Additionally, I've been trying to increase the speed at which I write articles, so why not kill 2 birds with one stone, and write an article on the agent I created to help me in writing it?

-- **INSERT IMAGE OF ARTICLE-WRITING-SEPTION** --

In this article, I tackle an age-old developer's quandary - how can I over-engineer a simple process to attempt and make it more efficient? 

With that in mind, in this guide, we will explore:

*   **AI agents in a nutshell:** What they are & what distinguishes different techniques.
*   **Creating the agent**: A deep dive into the step-by-step process of building your own React AI agent for article writing.
*   **Challenges, Lessons Learned & Future Iterations**: Practical insights and debugging tips gained throughout the development process.

## AI Agents - What are they

-- **INSERT DRAWING OF SECRET AGENT** --

Before you discuss any subject with another, you need to make sure that you're both speaking the same language. 

With that in mind, let's dive into some quick explanations of different key concepts of an agentic workflow. 

### 1. AI Agent

An umbrella term that encompasses a wide range of different techniques, an agent is an entity that processes inputs from its environment, evaluates them, and then reacts. 

This can take the form of an incredibly complex service, but can also be very mundane. Take a thermostat for example - It takes in the temperature, evaluates it against its configurations, and makes changes to the power allocated to heating accordingly.  

### 2. ReAct (Reason + Act) Agent

(Yes, I also was confused the first time I heard of this concept. No, it does not have anything to do with WebDev.)

An issue with agents is that they can be quite rigid, or need to follow a pre-defined workflow. Taking the example of the thermostat, it's quite good at processing temperature inputs, but would not know what to do if there's high humidity in your house without it being programmed to do so.

In a more modern example, with an LLM, we can program a series of actions to be done in sequence based on an input, but it's more complex to create an agent that will **choose** which action should be done in what order depending on the input. 

To resolve this, [an article was written in 2023](https://arxiv.org/pdf/2210.03629) which discusses chain-of-thought processing, where an LLM breaks down a complex prompt into a series of steps, and then at each step, evaluates what would be the best action to take given it's available tooling before evaluating the output and subsequently chooses the next action to perform.

-- **INSERT IMAGE OF REACT AGENT** --

This imitates more "human-like" reasoning using chain-of-thought (CoI), which follows the same pattern of action-evaluation. For example:
- You're hungry. You want to make yourself dinner.
- First, you need to lookup a recipe online
- Then, you need to check in your fridge, and validate if you have all the ingredients.
- If you do, then you can start cooking, and serve!

Let's take this example and use it to highlight different components of our architecture:

*   **Main node (agent):** The core of the agent, responsible for reasoning and decision-making.
*   **Tools:** External resources or functions that the agent can use to interact with the environment.
*   **Operational process:**
    1.  **Input/Query:** The agent receives an initial query or task.
    2.  **Planning (Reasoning):** The agent analyzes the query and formulates a plan to achieve the desired outcome. This involves reasoning about the available tools and knowledge.
    3.  **Action:** Based on the plan, the agent selects and executes an action. This might involve using a tool, querying an external API, or interacting with the environment.
    4.  **Observation:** The agent observes the result of the action. This could be the output of a tool, the response from an API, or a change in the environment.
    5.  **Reflection:** The agent reflects on the observation and updates its plan based on the new information. This step helps the agent adapt to unexpected results or refine its strategy.
    6.  **Repeat:** The agent repeats the planning, action, observation, and reflection steps until the task is completed or a satisfactory solution is found.

### Chain-of-Thought (CoT) Prompting

Chain-of-Thought (CoT) prompting is a technique that enhances the reasoning abilities of large language models by encouraging them to break down complex problems into a series of smaller, more manageable steps. By explicitly reasoning through the problem, the agent can arrive at more accurate and reliable solutions.

## Creating the Agent

### Objective

The goal is to create an agent that will streamline the article writing process.

### My Current Process

1.  **Write an outline:**
    *   Initial first draft in nested bullet-points.
    *   Copy-paste into Gemini for feedback & suggestions.
    *   Copy-back into Notion.
    *   Re-write 80% of it, keeping the nuggets.
    *   Repeat.
2.  **Write the article:**
    *   Take outline, paste in Gemini, generate the article.
    *   Copy back in Notion, gut and re-write.
    *   Re-pass in Gemini.
    *   Repeat.

This process, while effective, can be time-consuming.

### The Value of This Process

*   Get suggestions for expressions, turns of phrase, and structure.
*   Perform additional research.
*   Speed up generation of skeleton.
*   Easily process different types of artifacts (example - code).

### How We're Going to Re-produce This

We'll create an agent that can interact with files (Outline.md, Article.md) within a project directory and access the internet for additional information. For now, we'll interact with the agent through a CLI.

### Step-by-Step Guide

This implementation is heavily inspired by [this LangGraph agents article](https://langchain-ai.github.io/langgraph/agents/agents/).

1.  **Set Up Your Project Structure**

    Start by creating the following directory structure:

    ```
your-react-agent/
├── pyproject.toml
├── .env
├── main.py
├── workflow.py
├── tools.py
└── logging_config.py
    ```
2.  **Install Dependencies**

    Create a `pyproject.toml` file with the following dependencies:

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
3.  **Create Environment Configuration**

    Create a `.env` file and add your Google API key:

    ```env
GOOGLE_API_KEY=your_google_api_key_here
    ```
4.  **Set Up Logging**

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
5.  **Define Your Tools**

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

## Challenges and Lessons Learned

INSERT MORE CHALLENGES HERE

### A note on working with Cursor

Leveraged cursor to build application

Was fun, but came with unexpected issues regarding generating complex, un-flexible solutions that were hard to amend

[In pragmatic engineer](https://newsletter.pragmaticengineer.com/p/cursor-makes-developers-less-effective), can see that cursor can actually lower productivity when not well trained on its usage

Keep your eyes out for a longer article on this subject

## In future iterations:

*   In-memory storage to amend behaviour over time
    *   Integrate versionning to showcase edits over time, and re-ingest as context to learn my style
*   Fine-tune research performance
*   Integrate in UI to avoid usage of IDE
*   Better reference management

## Conclusion

In this guide, we've walked through the process of building a React AI agent for article writing. By leveraging tools like LangChain and LangGraph, you can create intelligent agents that streamline your workflow and enhance your productivity.

## References

*   ReAct: Synergizing Reasoning and Acting in Language Models
    *   Summary:
        *   The ReAct paper introduces a novel approach to language modeling that combines reasoning and acting. It proposes that language models can be more effective in complex tasks if they can not only generate text but also interact with an environment (e.g., a knowledge base or a search engine) to gather information and refine their reasoning process. The core idea is to interleave reasoning steps (thoughts) with actions that allow the model to gather more information, enabling it to handle tasks requiring more than just memorized knowledge.
    *   Key Contributions:
        *   The ReAct Framework: The paper presents a framework for training language models to perform reasoning and acting in a synergistic manner.
        *   Improved Performance on Complex Tasks: The paper demonstrates that ReAct agents outperform traditional language models on a range of tasks, including question answering, fact verification, and commonsense reasoning.
        *   Enhanced Interpretability: By explicitly modeling the reasoning process, ReAct agents provide more interpretable and transparent decision-making compared to black-box language models.
        *   Addressing Hallucination: The ability to gather information from external sources helps ReAct agents mitigate the problem of hallucination (generating false or misleading information), which is a common issue in large language models.
    *   Link: https://arxiv.org/abs/2210.03629
*   Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
    *   Wei et al. 2022
*   https://www.ibm.com/think/topics/chain-of-thoughts
    *   Summary: This article covers the fundamentals of chain of thought prompting with IBM Granite 3.3 Instruct models, highlighting how it encourages step-by-step reasoning to solve complex tasks.
*   https://www.ibm.com/think/topics/react-agent#1287801558
    *   Summary: This resource discusses ReAct agents, which improvise and act fast, figuring things out in real time.
*   https://spr.com/comparing-react-and-rewoo-two-frameworks-for-building-ai-agents-in-generative-ai/
    *   Summary: This blog post compares ReAct (Reasoning and Action) and ReWOO (Reasoning Without Observations) as two popular frameworks for building AI agents in generative AI.