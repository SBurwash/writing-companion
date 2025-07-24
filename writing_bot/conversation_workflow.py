from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END, START
from langchain.globals import set_verbose
from .session_manager import SessionManager
from .article_manager import ArticleManager
from IPython.display import Image, display
import click
import google.generativeai as genai
import os

set_verbose(True)
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
        print(self.workflow.get_graph().draw_mermaid())
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow.
        
        Returns:
            StateGraph workflow
        """
        # Define the state schema
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_input", self._analyze_input)
        workflow.add_node("research_topic", self._research_topic)
        workflow.add_node("suggest_outline_updates", self._suggest_outline_updates)
        workflow.add_node("apply_outline_updates", self._apply_outline_updates)
        workflow.add_node("generate_response", self._generate_response)
        
        # Define edges
        workflow.add_edge(START, "analyze_input")
        workflow.add_edge("analyze_input", "research_topic")
        workflow.add_edge("research_topic", "suggest_outline_updates")
        workflow.add_edge("suggest_outline_updates", "apply_outline_updates")
        workflow.add_edge("apply_outline_updates", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_input",
            self._route_after_analysis,
            {
                "research": "research_topic",
                "direct_response": "generate_response",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "suggest_outline_updates",
            self._route_after_suggestions,
            {
                "apply_updates": "apply_outline_updates",
                "skip_updates": "generate_response",
                "end": END
            }
        )
        
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
        
        # Analyze the input using LLM
        analysis_prompt = f"""
        Analyze this user input and determine the appropriate action:
        
        User input: "{user_input}"
        
        Available actions:
        1. "research" - User wants to research a topic
        2. "direct_response" - User wants a direct response/feedback
        3. "end" - User wants to end the conversation
        
        Respond with only the action name.
        """
        
        response = self.llm.generate_content(analysis_prompt)
        action = response.text.strip().lower()
        
        # Update session state
        self.session_manager.update_state("analyzing_input", {"detected_action": action})
        
        return {
            **state,
            "detected_action": action,
            "analysis_complete": True
        }
    
    def _route_after_analysis(self, state: WorkflowState) -> str:
        """Route to next node based on analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node name
        """
        action = state.get("detected_action", "direct_response")
        
        if "research" in action:
            return "research"
        elif "end" in action:
            return "end"
        else:
            return "direct_response"
    
    def _research_topic(self, state: WorkflowState) -> WorkflowState:
        """Research a topic and store results.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        user_input = state["user_input"]
        
        # Extract research topic from user input
        topic_prompt = f"""
        Extract the research topic from this user input:
        "{user_input}"
        
        Respond with only the topic name.
        """
        
        response = self.llm.generate_content(topic_prompt)
        topic = response.text.strip()
        
        # Perform research using Gemini
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
            "research_topic": topic,
            "research_data": research_data,
            "research_complete": True
        }
    
    def _suggest_outline_updates(self, state: WorkflowState) -> WorkflowState:
        """Suggest outline updates based on research.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        # Get current outline
        files = self.article_manager.get_project_files(self.project_name)
        outline_content = self.article_manager.read_file(files['outline'])
        
        # Get research data
        research_data = state.get("research_data", {})
        topic = state.get("research_topic", "")
        
        # Generate suggestions
        suggestion_prompt = f"""
        Based on the research about "{topic}", suggest updates to this outline:
        
        Current Outline:
        {outline_content}
        
        Research Findings:
        {research_data.get('content', 'No research data available')}
        
        Suggest specific updates to improve the outline based on the research.
        Include:
        1. New sections to add
        2. Existing sections to modify
        3. Key points to include
        4. Structure improvements
        
        Format as a clear list of suggestions.
        """
        
        response = self.llm.generate_content(suggestion_prompt)
        suggestions = response.text
        
        # Ask user if they want to apply suggestions
        click.echo(f"\n🔍 Research completed for: {topic}")
        click.echo(f"📋 Suggestions for outline updates:")
        click.echo("=" * 50)
        click.echo(suggestions)
        click.echo("=" * 50)
        
        apply_updates = click.confirm("Would you like to apply these outline updates?")
        
        # Store suggestions in session
        self.session_manager.add_pending_action(
            "update_outline",
            f"Apply research-based suggestions for {topic}",
            {"suggestions": suggestions, "topic": topic}
        )
        
        return {
            **state,
            "suggestions": suggestions,
            "apply_updates": apply_updates
        }
    
    def _route_after_suggestions(self, state: WorkflowState) -> str:
        """Route after suggesting outline updates.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node name
        """
        if state.get("apply_updates", False):
            return "apply_updates"
        else:
            return "skip_updates"
    
    def _apply_outline_updates(self, state: WorkflowState) -> WorkflowState:
        """Apply the suggested outline updates.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        suggestions = state.get("suggestions", "")
        
        # Generate updated outline
        update_prompt = f"""
        Update this outline based on the suggestions:
        
        Current Outline:
        {self.article_manager.read_file(self.article_manager.get_project_files(self.project_name)['outline'])}
        
        Suggestions:
        {suggestions}
        
        Provide the complete updated outline that incorporates the suggestions.
        """
        
        response = self.llm.generate_content(update_prompt)
        updated_outline = response.text
        
        # Update the outline file
        outline_path = self.article_manager.get_project_files(self.project_name)['outline']
        self.article_manager.write_file(outline_path, updated_outline)
        
        # Update session
        self.session_manager.update_state("outline_updated", {"updates_applied": True})
        self.session_manager.clear_pending_actions()
        
        # Add to conversation history
        self.session_manager.add_conversation_entry(
            "assistant",
            "Outline updated based on research suggestions",
            {"updates_applied": True}
        )
        
        return {
            **state,
            "outline_updated": True,
            "updated_outline": updated_outline
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
        
        # Generate contextual response
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