from gqlalchemy import Memgraph
from gqlalchemy import Node
import click
from .markdown_ingest import find_article_projects, read_markdown_file
from .graph_schema import Article, Outline
import os
import uuid

@click.command()
def main():
    try:
        mg = Memgraph()
        mg.execute("RETURN 1")
        print("Successfully connected to Memgraph!")
    except Exception as e:
        print(f"Failed to connect to Memgraph: {e}")
        return

    # Ingest all articles and outlines automatically
    projects = find_article_projects()
    for project in projects:
        article_id = str(uuid.uuid4())
        outline_id = str(uuid.uuid4())
        article_title = project['name'].replace('_', ' ').title()
        article_path = project['article_path']
        outline_path = project['outline_path']
        # Create Article node
        article_node = Article(id=article_id, title=article_title, path=article_path)
        mg.save_node(article_node)
        # Create Outline node
        outline_node = Outline(id=outline_id, article_id=article_id, path=outline_path)
        mg.save_node(outline_node)
        print(f"Ingested article: {article_title}") 