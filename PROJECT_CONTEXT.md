# Project Context: Writing Bot with Memgraph & gqlalchemy

## Purpose
A CLI tool to help you write articles with style, process memory, and reference suggestions, powered by Memgraph (graph DB) and gqlalchemy (Python client).

## Current Architecture
- **CLI entry point:** `cli.py` (calls `writing_bot.main:main()`)
- **Main logic:** `writing_bot/main.py`
- **Graph schema:** `writing_bot/graph_schema.py` (Node models for Article, Outline, StyleElement, ProcessStep, Reference)
- **Markdown ingestion:** `writing_bot/markdown_ingest.py` (scans `writing_bot/articles/` for article/outline pairs)
- **Articles directory:** `writing_bot/articles/` (each project: subdir with `article.md` and `outline.md`)

## Dependencies
- Python >=3.10,<4.0
- Memgraph (running in Docker or natively)
- gqlalchemy==1.7.0 (Python client for Memgraph)
- click (for CLI)

## Progress
- [x] Poetry project setup
- [x] Memgraph connection via CLI
- [x] Graph schema for articles, outlines, style/process, references
- [x] Markdown ingestion utility
- [x] Automatic ingestion of all articles/outlines into Memgraph
- [x] Downgraded gqlalchemy to 1.7.0 for compatibility

## Next Steps (when resuming)
- Add relationships between nodes (e.g., Article <-> Outline, Article <-> StyleElement, etc.)
- Implement style/process extraction from Markdown
- Build interactive CLI chat loop
- Add reference suggestion (web search, graph traversal)
- Enhance memory and learning over time

## How to Resume
1. Ensure Memgraph is running (e.g., `docker run -p 7687:7687 -p 3000:3000 memgraph/memgraph`)
2. Activate poetry shell or use `poetry run python cli.py`
3. Review this file and codebase for context

---
_Last updated: break after initial ingestion and schema setup_ 