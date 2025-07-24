# Article Writing CLI

A CLI tool to help you write articles in Cursor by leveraging Gemini CLI for content generation, editing, and research. The tool works with outlines and provides automatic versioning through git.

## Features

- **Outline-based workflow**: Start with an outline, get AI feedback
- **Gemini integration**: Leverage Google's Gemini for content review and suggestions
- **Git versioning**: Automatic tracking of all changes
- **Project management**: Easy project initialization and management
- **Free-form review**: Natural language requests for feedback

## Quick Start

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Set up Gemini CLI:
   ```bash
   # Set your Google AI API key
   export GOOGLE_API_KEY="your-api-key-here"
   ```

3. Initialize a new article project:
   ```bash
   poetry run python cli.py init my-article
   ```

4. Set your current project (optional):
   ```bash
   export PROJECT_NAME="my-article"
   ```

5. Start working with AI assistance:
   ```bash
   # Quick review
   poetry run python cli.py review "please review my outline and suggest improvements"
   
   # Conversational session
   poetry run python cli.py chat
   
   # Check status and commit
   poetry run python cli.py status
   poetry run python cli.py commit "Updated outline based on feedback"
   ```

## Commands

- `init <project_name>` - Initialize new article project
- `list` - List all available projects
- `status [project_name]` - Show project status and git history
- `commit <message> [project_name]` - Commit changes with custom message
- `review <request> [--project project_name]` - Review project with free-form requests
- `chat [project_name]` - Start conversational session with AI assistant

## Environment Variables

- `GOOGLE_API_KEY` - Your Google AI API key (required for review functionality)
- `PROJECT_NAME` - Default project name (optional, allows omitting project parameter)

## Examples

```bash
# Create a new project
poetry run python cli.py init my-blog-post

# Set as default project
export PROJECT_NAME="my-blog-post"

# Review your outline
poetry run python cli.py review "review my outline structure"

# Check project status
poetry run python cli.py status

# Commit changes
poetry run python cli.py commit "Updated outline based on feedback"

# Review with specific project
poetry run python cli.py review "give me writing tips" --project my-blog-post

# Start conversational session
poetry run python cli.py chat

# In the chat session, you can:
# - Ask for research: "research data governance trends"
# - Get feedback: "review my outline structure"
# - Request suggestions: "suggest improvements for my introduction"
``` 