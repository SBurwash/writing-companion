# Project Context: Article Writing CLI with Gemini

## Purpose
A CLI tool to help you write articles in Cursor by leveraging Gemini CLI for content review and feedback. The tool works with outlines and provides versioning through git.

## Core Workflow
1. **Write an outline** in markdown format
2. **Use CLI commands** to interact with Gemini for:
   - Reviewing outlines and content
   - Getting feedback on structure
   - Receiving writing suggestions
   - Identifying gaps and improvements
3. **Git versioning** tracks all changes automatically

## Architecture
- **CLI entry point:** `cli.py` (calls `writing_bot.main:main()`)
- **Main logic:** `writing_bot/main.py` (CLI commands and Gemini integration)
- **Article management:** `writing_bot/article_manager.py` (file operations, git integration)
- **Gemini integration:** `writing_bot/gemini_client.py` (API calls to Gemini CLI)
- **Articles directory:** `writing_bot/articles/` (each project: subdir with `outline.md` and `article.md`)

## Dependencies
- Python >=3.10,<4.0
- Gemini CLI (for content review)
- click (for CLI interface)
- gitpython (for version control)
- pyyaml (for configuration)

## CLI Commands
- `init <project_name>` - Initialize new article project
- `list` - List all available projects
- `status [project_name]` - Show project status and git history
- `commit <message> [project_name]` - Commit changes with custom message
- `review <request> [--project project_name]` - Review project with free-form requests

## File Structure
```
writing_bot/articles/
├── project_name/
│   ├── outline.md      # Original outline
│   ├── article.md      # Generated/edited content
│   ├── config.yaml     # Project configuration
│   └── .git/           # Git repository for versioning
```

## Environment Variables
- `GOOGLE_API_KEY` - Google AI API key (required for review functionality)
- `PROJECT_NAME` - Default project name (optional)

## Progress
- [x] Project setup and dependencies
- [x] Basic CLI structure
- [x] Gemini CLI integration
- [x] Article project management
- [x] Git versioning integration
- [x] Core CLI commands
- [x] Free-form review system
- [x] Environment variable support

## Current Status
The project is now simplified and focused on:
1. **Project Management**: Create and manage article projects
2. **AI Review**: Get feedback on outlines and content using natural language
3. **Version Control**: Track all changes with git
4. **Flexible Workflow**: Use environment variables for convenience

---
_Simplified CLI-based article writing with Gemini review and git versioning_ 