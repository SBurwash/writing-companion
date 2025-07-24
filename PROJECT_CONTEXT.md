# Project Context: Article Writing CLI with Gemini

## Purpose
A CLI tool to help you write articles in Cursor by leveraging Gemini CLI for content generation, editing, and research. The tool works with outlines and provides versioning through git.

## Core Workflow
1. **Write an outline** in markdown format
2. **Use CLI commands** to interact with Gemini for:
   - Expanding sections
   - Rewriting content
   - Research and fact-checking
   - Style improvements
   - Content suggestions
3. **Git versioning** tracks all changes automatically

## Architecture
- **CLI entry point:** `cli.py` (calls `writing_bot.main:main()`)
- **Main logic:** `writing_bot/main.py` (CLI commands and Gemini integration)
- **Article management:** `writing_bot/article_manager.py` (file operations, git integration)
- **Gemini integration:** `writing_bot/gemini_client.py` (API calls to Gemini CLI)
- **Articles directory:** `writing_bot/articles/` (each project: subdir with `outline.md` and `article.md`)

## Dependencies
- Python >=3.10,<4.0
- Gemini CLI (for content generation)
- click (for CLI interface)
- gitpython (for version control)
- pyyaml (for configuration)

## CLI Commands (planned)
- `init <project_name>` - Initialize new article project
- `expand <section>` - Expand outline section with Gemini
- `rewrite <section>` - Rewrite existing content
- `research <topic>` - Get research and facts from Gemini
- `improve <section>` - Improve writing style and flow
- `status` - Show current project status and git history
- `commit <message>` - Commit changes with custom message

## File Structure
```
writing_bot/articles/
├── project_name/
│   ├── outline.md      # Original outline
│   ├── article.md      # Generated/edited content
│   └── .git/           # Git repository for versioning
```

## Progress
- [ ] Project setup and dependencies
- [ ] Basic CLI structure
- [ ] Gemini CLI integration
- [ ] Article project management
- [ ] Git versioning integration
- [ ] Core CLI commands

## Next Steps
1. Set up new project structure
2. Install and configure Gemini CLI
3. Create basic CLI framework
4. Implement article project management
5. Add Gemini integration for content generation
6. Integrate git versioning

---
_New direction: Simplified CLI-based article writing with Gemini and git versioning_ 