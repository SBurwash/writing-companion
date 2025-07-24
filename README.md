# Article Writing CLI

A CLI tool to help you write articles in Cursor by leveraging Gemini CLI for content generation, editing, and research. The tool works with outlines and provides automatic versioning through git.

## Features

- **Outline-based workflow**: Start with an outline, expand with AI
- **Gemini integration**: Leverage Google's Gemini for content generation
- **Git versioning**: Automatic tracking of all changes
- **CLI commands**: Easy commands for expanding, rewriting, and researching

## Quick Start

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Set up Gemini CLI:
   ```bash
   # Follow Gemini CLI setup instructions
   ```

3. Initialize a new article project:
   ```bash
   poetry run python cli.py init my-article
   ```

4. Start writing with AI assistance:
   ```bash
   poetry run python cli.py expand my-article introduction
   poetry run python cli.py research "latest trends"
   poetry run python cli.py improve my-article conclusion
   poetry run python cli.py review my-article "please review my outline and suggest improvements"
   ```

## Commands

- `init <project_name>` - Initialize new article project
- `list` - List all available projects
- `expand <project> <section>` - Expand outline section with Gemini
- `rewrite <project> <section> <instruction>` - Rewrite existing content
- `research <topic>` - Get research and facts from Gemini
- `improve <project> <section>` - Improve writing style and flow
- `review <project> <request>` - Review project with free-form requests
- `status <project>` - Show current project status and git history
- `commit <project> <message>` - Commit changes with custom message
- `outline <project>` - View project outline
- `article <project>` - View project article content 