import google.generativeai as genai
import os
from typing import Optional, Dict, Any


class GeminiClient:
    """Client for interacting with Google's Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini client.
        
        Args:
            api_key: Google AI API key. If not provided, will look for GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def review_with_context(self, request: str, outline_content: str, article_content: str = "", project_name: str = "") -> str:
        """Handle free-form review requests with project context.
        
        Args:
            request: The user's review request (e.g., "review my outline", "give feedback on structure")
            outline_content: Content of the outline.md file
            article_content: Content of the article.md file (if exists)
            project_name: Name of the project for context
            
        Returns:
            Review feedback and suggestions
        """
        prompt = f"""
        You are a professional writing consultant and editor. A user has requested: "{request}"
        
        Project: {project_name}
        
        Here is the current outline:
        {outline_content}
        
        Here is the current article content (if any):
        {article_content if article_content else "No article content yet - only outline exists"}
        
        Please provide a comprehensive review and feedback based on the user's request. Consider:
        
        - Structure and organization
        - Completeness of the outline
        - Logical flow and progression
        - Clarity of main points
        - Potential gaps or missing elements
        - Suggestions for improvement
        - Writing style and tone consistency
        
        Provide specific, actionable feedback that the user can implement. Be constructive and encouraging.
        
        Format your response in a clear, organized manner with sections for:
        1. Overall Assessment
        2. Strengths
        3. Areas for Improvement
        4. Specific Recommendations
        5. Next Steps
        """
        
        response = self.model.generate_content(prompt)
        return response.text 