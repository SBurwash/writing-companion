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
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def expand_section(self, outline_section: str, context: str = "") -> str:
        """Expand an outline section into full content.
        
        Args:
            outline_section: The outline section to expand
            context: Additional context about the article
            
        Returns:
            Expanded content for the section
        """
        prompt = f"""
        You are a professional article writer. Expand the following outline section into well-written, engaging content.
        
        Article context: {context}
        
        Outline section: {outline_section}
        
        Please write 2-3 paragraphs that:
        - Maintain the key points from the outline
        - Are engaging and well-structured
        - Use clear, professional language
        - Include relevant examples or explanations where appropriate
        
        Return only the expanded content, no additional formatting.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def rewrite_content(self, content: str, instruction: str = "improve") -> str:
        """Rewrite existing content based on instructions.
        
        Args:
            content: The content to rewrite
            instruction: Specific instruction for rewriting (e.g., "make more engaging", "simplify", "add more detail")
            
        Returns:
            Rewritten content
        """
        prompt = f"""
        You are a professional editor. Rewrite the following content according to this instruction: "{instruction}"
        
        Content to rewrite:
        {content}
        
        Please provide the rewritten version that follows the instruction while maintaining the core message and key information.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def research_topic(self, topic: str) -> str:
        """Get research and facts about a topic.
        
        Args:
            topic: The topic to research
            
        Returns:
            Research findings and facts
        """
        prompt = f"""
        You are a research assistant. Provide current, factual information about: {topic}
        
        Please include:
        - Key facts and statistics
        - Recent developments or trends
        - Relevant examples or case studies
        - Sources or references where possible
        
        Format the response in a clear, organized manner suitable for inclusion in an article.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def improve_style(self, content: str, style_notes: str = "") -> str:
        """Improve the writing style and flow of content.
        
        Args:
            content: The content to improve
            style_notes: Specific style preferences or notes
            
        Returns:
            Style-improved content
        """
        prompt = f"""
        You are a professional writing coach. Improve the style, flow, and readability of the following content.
        
        Style preferences: {style_notes if style_notes else "Professional, engaging, clear"}
        
        Content to improve:
        {content}
        
        Please enhance:
        - Sentence structure and flow
        - Word choice and clarity
        - Engagement and readability
        - Professional tone
        
        Return the improved version while maintaining all key information and meaning.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
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