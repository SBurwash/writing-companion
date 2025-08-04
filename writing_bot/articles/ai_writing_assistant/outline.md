# Outline: React AI Agent

*   **Introduction**
    *   AI is the name on the town right now
    *   Lots of talk about the "what", but very little on the "how"
    *   Recently trying to up my article writing game - what better way than to do a tutorial on writing an AI writing assistant?
    *   In this article
        *   AI agent in a nutshell
        *   React AI agent specifically
        *   Libraries, Frameworks & Tools (Langchain, LangGraph & LangSmith)

*   **Understanding AI Agents**
    *   AI Agent -> Insert definition
        *   Agent: An entity that perceives its environment through sensors and acts upon that environment through effectors. In the context of AI, an agent typically refers to a software program that can autonomously perform tasks to achieve specific goals.
        *   ReAct Agent: An agent that combines reasoning and acting, allowing it to interact with an environment to solve complex tasks. Unlike traditional agents that primarily focus on pre-defined actions, ReAct agents interleave reasoning traces and actions, enabling more dynamic and human-like problem-solving. This allows them to handle situations not explicitly programmed in advance.
        *   Comparison to an intern, or well-trained monkey
    *   ReAct (Reason + Act) **agent**
        *   Definition
        *   Components
            *   Main node (agent)
            *   Tools
        *   Operational process
            *   Input/Query: The agent receives an initial query or task.
            *   Planning (Reasoning): The agent analyzes the query and formulates a plan to achieve the desired outcome. This involves reasoning about the available tools and knowledge.
            *   Action: Based on the plan, the agent selects and executes an action. This might involve using a tool, querying an external API, or interacting with the environment.
            *   Observation: The agent observes the result of the action. This could be the output of a tool, the response from an API, or a change in the environment.
            *   Reflection: The agent reflects on the observation and updates its plan based on the new information. This step helps the agent adapt to unexpected results or refine its strategy.
            *   Repeat: The agent repeats the planning, action, observation, and reflection steps until the task is completed or a satisfactory solution is found.
    *   Chain-of-Thought (CoT) Prompting
        *   Explanation of Chain-of-Thought prompting and its benefits

* **Creating the agent**
  * Objective - Create an agent that will enable me to write articles
    * My current process
      * Write an outline
        * Initial first draft in nested bullet-points
        * Copy-paste into gemini for feedback & suggestions
        * Copy-back into notion
        * Re-write 80% of it, keeping the nuggets
        * Repeat
      * Once that's done, write the article
        * Take outline, paste in gemini, generate the article
        * Copy back in Notion, gut and re-write
        * Re-pass in Gemini
        * And round we go
    * The value of this process
      * Get suggestions for expressions, turns of phrase, structure
      * Perform additional research
      * Speed up generation of skeleton
      * Easily process different types of artifacts (example - code)
    * How we're going to re-produce this
      * Write articles in IDE - Each article is in its own sub-folder, with 2 files:
        *  Outline.md
        *  Article.md
     *  Create an agent that can
        *  Interact with the files to make edits
        *  Interact with the internet to get additional information
     *  How to interact with them?
        *  For now - CLI
  *  Step-by-step guide
     *  

*   **Challenges and Lessons Learned:**
    *   A dedicated section on the challenges you faced throughout the entire process.
    *   Specific lessons you learned about AI agents, React development, and the writing assistant domain.
    *   Debugging tips and troubleshooting techniques.

*   **Future Directions:**
    *   Your plans for the future of the writing assistant. What features do you want to add?
    *   Areas for improvement and optimization.
    *   How you plan to address the challenges you identified.



*   **Conclusion**
    *   Recap of the key steps
    *   Potential future directions and improvements

* **A note on working with Cursor**
  * Leveraged cursor to build application
  * Was fun, but came with unexpected issues regarding generating complex, un-flexible solutions that were hard to amend
  * [In pragmatic engineer](https://newsletter.pragmaticengineer.com/p/cursor-makes-developers-less-effective), can see that cursor can actually lower productivity when not well trained on its usage
  * Keep your eyes out for a longer article on this subject


* **References**
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
  *  https://www.ibm.com/think/topics/chain-of-thoughts
  *  https://www.ibm.com/think/topics/react-agent#1287801558
  *  https://spr.com/comparing-react-and-rewoo-two-frameworks-for-building-ai-agents-in-generative-ai/