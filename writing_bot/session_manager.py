import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class SessionManager:
    """Manages conversation sessions and state for each project."""
    
    def __init__(self, project_path: Path):
        """Initialize session manager for a project.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        self.session_file = project_path / "session.json"
        self.conversation_file = project_path / "conversation.json"
        
    def get_session(self) -> Dict[str, Any]:
        """Get current session data.
        
        Returns:
            Session data dictionary
        """
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize new session
            session = {
                "project_name": self.project_path.name,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "current_state": "idle",
                "context": {},
                "research_data": {},
                "pending_actions": [],
                "conversation_history": []
            }
            self.save_session(session)
            return session
    
    def save_session(self, session: Dict[str, Any]) -> None:
        """Save session data to file.
        
        Args:
            session: Session data to save
        """
        session["last_updated"] = datetime.now().isoformat()
        with open(self.session_file, 'w') as f:
            json.dump(session, f, indent=2)
    
    def update_state(self, new_state: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Update the current session state.
        
        Args:
            new_state: New state name
            context: Additional context data
        """
        session = self.get_session()
        session["current_state"] = new_state
        if context:
            session["context"].update(context)
        self.save_session(session)
    
    def add_research_data(self, topic: str, data: Dict[str, Any]) -> None:
        """Add research data to session.
        
        Args:
            topic: Research topic
            data: Research data
        """
        session = self.get_session()
        session["research_data"][topic] = {
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.save_session(session)
    
    def get_research_data(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get research data for a topic.
        
        Args:
            topic: Research topic
            
        Returns:
            Research data if exists, None otherwise
        """
        session = self.get_session()
        return session["research_data"].get(topic)
    
    def add_pending_action(self, action: str, description: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Add a pending action to the session.
        
        Args:
            action: Action type (e.g., "update_outline", "research_topic")
            description: Human-readable description
            data: Action-specific data
        """
        session = self.get_session()
        pending_action = {
            "action": action,
            "description": description,
            "data": data or {},
            "created_at": datetime.now().isoformat()
        }
        session["pending_actions"].append(pending_action)
        self.save_session(session)
    
    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """Get all pending actions.
        
        Returns:
            List of pending actions
        """
        session = self.get_session()
        return session["pending_actions"]
    
    def clear_pending_actions(self) -> None:
        """Clear all pending actions."""
        session = self.get_session()
        session["pending_actions"] = []
        self.save_session(session)
    
    def add_conversation_entry(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a conversation entry to the history.
        
        Args:
            role: "user" or "assistant"
            content: Message content
            metadata: Additional metadata
        """
        session = self.get_session()
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        session["conversation_history"].append(entry)
        self.save_session(session)
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of conversation entries
        """
        session = self.get_session()
        history = session["conversation_history"]
        if limit:
            history = history[-limit:]
        return history
    
    def get_context_summary(self) -> str:
        """Get a summary of the current session context.
        
        Returns:
            Context summary string
        """
        session = self.get_session()
        summary_parts = []
        
        summary_parts.append(f"Current State: {session['current_state']}")
        
        if session["context"]:
            summary_parts.append("Context:")
            for key, value in session["context"].items():
                summary_parts.append(f"  {key}: {value}")
        
        if session["research_data"]:
            summary_parts.append("Research Topics:")
            for topic in session["research_data"].keys():
                summary_parts.append(f"  - {topic}")
        
        if session["pending_actions"]:
            summary_parts.append("Pending Actions:")
            for action in session["pending_actions"]:
                summary_parts.append(f"  - {action['description']}")
        
        return "\n".join(summary_parts) 