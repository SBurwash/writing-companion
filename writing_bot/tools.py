import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

from langchain_community.agent_toolkits import FileManagementToolkit

# Setup module logger
logger = logging.getLogger(__name__)


def get_file_management_tools():
    """Get file management tools restricted to the articles directory."""
    # Get the current working directory (project root)
    project_root = Path.cwd()
    articles_dir = project_root / "writing_bot" / "articles"
    
    # Ensure the articles directory exists
    articles_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Initializing FileManagementToolkit with root_dir: {articles_dir}")
    
    # Create toolkit restricted to articles directory
    file_toolkit = FileManagementToolkit(root_dir=str(articles_dir)).get_tools()
    
    logger.info(f"Loaded {len(file_toolkit)} file management tools")
    return file_toolkit
