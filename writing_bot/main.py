from gqlalchemy import Memgraph, Node, Relationship
import click
from .markdown_ingest import find_article_projects, read_markdown_file
from .graph_schema import Article, Outline, HasOutline, db
import os
import uuid


@click.command()
def main():
    # Clear the database before ingestion
    db.execute("MATCH (n) DETACH DELETE n;")
    print("Database cleared.")

    # Ingest all articles and outlines automatically
    projects = find_article_projects()
    for project in projects:
        print(project)
        article_id = str(uuid.uuid4())
        outline_id = str(uuid.uuid4())
        article_title = project['name'].replace('_', ' ').title()
        article_path = project['article_path']
        outline_path = project['outline_path']
        # Create Article node
        article_node = Article(id=article_id, title=article_title, path=article_path)
        # Save Article node and get internal _id
        article_node = db.save_node(article_node)
        # Create Outline node
        outline_node = Outline(id=outline_id, article_id=article_id, path=outline_path)
        # Save Outline node and get internal _id
        outline_node = db.save_node(outline_node)
        # Create HAS_OUTLINE relationship using internal Memgraph node IDs
        has_outline = Relationship(type="HAS_OUTLINE", _start_node_id=article_node._id, _end_node_id=outline_node._id)
        db.save_relationship(has_outline)
        print(f"Ingested article: {article_title} (with outline)") 