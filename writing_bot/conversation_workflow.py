from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END, START
from .session_manager import SessionManager
from .article_manager import ArticleManager
import click
import google.generativeai as genai
import os


class WorkflowState(TypedDict):
    """State schema for the conversation workflow."""
    user_input: str
    project_name: str
    detected_action: Optional[str]
    analysis_complete: Optional[bool]
    research_topic: Optional[str]
    research_data: Optional[Dict[str, Any]]
    research_complete: Optional[bool]
    suggestions: Optional[str]
    apply_updates: Optional[bool]
    outline_updated: Optional[bool]
    updated_outline: Optional[str]
    assistant_response: Optional[str]
    conversation_complete: Optional[bool]


class ConversationWorkflow:
    """LangGraph workflow for conversational article writing."""
    
    def __init__(self, session_manager: SessionManager, article_manager: ArticleManager, project_name: str):
        """Initialize the conversation workflow.
        
        Args:
            session_manager: Session manager for state
            article_manager: Article manager for file operations
            project_name: Name of the current project
        """
        self.session_manager = session_manager
        self.article_manager = article_manager
        self.project_name = project_name
        
        # Initialize LLM with direct Google API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.llm = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow.
        
        Returns:
            StateGraph workflow
        """
        # Define the state schema
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_input", self._analyze_input)
        workflow.add_node("generate_response", self._generate_response)
        
        # Define simple linear flow
        workflow.add_edge(START, "analyze_input")
        workflow.add_edge("analyze_input", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _analyze_input(self, state: WorkflowState) -> WorkflowState:
        """Analyze user input and determine next action.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        user_input = state["user_input"]
        
        # Add to conversation history
        self.session_manager.add_conversation_entry("user", user_input)
        
        # Check if this is a research request
        research_keywords = ["research", "find", "look up", "search", "investigate"]
        is_research = any(keyword in user_input.lower() for keyword in research_keywords)
        
        if is_research:
            # Extract research topic
            topic_prompt = f"""
            Extract the research topic from this user input:
            "{user_input}"
            
            Respond with only the topic name.
            """
            
            response = self.llm.generate_content(topic_prompt)
            topic = response.text.strip()
            
            # Perform research
            research_prompt = f"""
            Research the topic: {topic}
            
            Provide comprehensive information including:
            - Key facts and statistics
            - Recent developments
            - Relevant examples
            - Sources and references
            
            Format as structured data.
            """
            
            research_response = self.llm.generate_content(research_prompt)
            research_data = {
                "topic": topic,
                "content": research_response.text,
                "timestamp": "now"
            }
            
            # Store research data in session
            self.session_manager.add_research_data(topic, research_data)
            self.session_manager.update_state("research_complete", {"researched_topic": topic})
            
            # Add to conversation history
            self.session_manager.add_conversation_entry(
                "assistant", 
                f"Research completed for: {topic}",
                {"research_data": research_data}
            )
            
            return {
                **state,
                "detected_action": "research",
                "research_topic": topic,
                "research_data": research_data,
                "research_complete": True,
                "analysis_complete": True
            }
        else:
            # Direct response request
            return {
                **state,
                "detected_action": "direct_response",
                "analysis_complete": True
            }
    
    def _generate_response(self, state: WorkflowState) -> WorkflowState:
        """Generate final response to user.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with response
        """
        user_input = state["user_input"]
        context = self.session_manager.get_context_summary()
        detected_action = state.get("detected_action", "direct_response")
        
        if detected_action == "research":
            # Generate research-based response
            research_data = state.get("research_data", {})
            topic = state.get("research_topic", "")
            
            response_prompt = f"""
            Generate a helpful response about the research completed:
            
            User request: "{user_input}"
            Research topic: {topic}
            Research findings: {research_data.get('content', 'No data available')}
            
            Provide a comprehensive response that:
            1. Summarizes the key findings
            2. Suggests how this research could improve their article
            3. Offers specific recommendations for their outline
            
            Be helpful and actionable.
            """
        else:
            # Generate general response
            response_prompt = f"""
            Generate a helpful response to the user based on the current context:
            
            User input: "{user_input}"
            
            Current context:
            {context}
            
            Provide a helpful, contextual response that addresses the user's request.
            """
        
        response = self.llm.generate_content(response_prompt)
        assistant_response = response.text
        
        # Add to conversation history
        self.session_manager.add_conversation_entry("assistant", assistant_response)
        
        return {
            **state,
            "assistant_response": assistant_response,
            "conversation_complete": True
        }
    
    def run(self, user_input: str) -> WorkflowState:
        """Run the conversation workflow.
        
        Args:
            user_input: User's input message
            
        Returns:
            Workflow result
        """
        # Initialize state
        initial_state: WorkflowState = {
            "user_input": user_input,
            "project_name": self.project_name,
            "detected_action": None,
            "analysis_complete": None,
            "research_topic": None,
            "research_data": None,
            "research_complete": None,
            "suggestions": None,
            "apply_updates": None,
            "outline_updated": None,
            "updated_outline": None,
            "assistant_response": None,
            "conversation_complete": None
        }
        
        # Run the workflow
        result = self.workflow.invoke(initial_state)
        
        return result 