from gqlalchemy import Memgraph, Node, Relationship
import click
from .markdown_ingest import find_article_projects, read_markdown_file
from .graph_schema import Article, Outline, HasOutline, db, StyleElement, ProcessStep
from .markdown_analysis import extract_style_and_process
import os
import uuid


@click.command()
def main():
    # Clear the database before ingestion
    db.execute("MATCH (n) DETACH DELETE n;")
    print("Database cleared.")

    projects = find_article_projects()
    for project in projects:
        article_id = str(uuid.uuid4())
        outline_id = str(uuid.uuid4())
        article_title = project['name'].replace('_', ' ').title()
        article_path = project['article_path']
        outline_path = project['outline_path']
        # Create Article node
        article_node = Article(id=article_id, title=article_title, path=article_path)
        article_node = db.save_node(article_node)
        # Create Outline node
        outline_node = Outline(id=outline_id, article_id=article_id, path=outline_path)
        outline_node = db.save_node(outline_node)
        # Create HAS_OUTLINE relationship
        has_outline = Relationship(type="HAS_OUTLINE", _start_node_id=article_node._id, _end_node_id=outline_node._id)
        db.save_relationship(has_outline)
        print(f"Ingested article: {article_title} (with outline)")

        # --- Style/Process Extraction ---
        article_text = read_markdown_file(article_path)
        style_elements, process_steps = extract_style_and_process(article_text)
        # Add StyleElement nodes and relationships
        for style in style_elements:
            style_id = f"style_{style}"
            result = db.execute_and_fetch(
                "MATCH (n:StyleElement {id: $id}) RETURN n",
                {"id": style_id}
            )
            style_node = next(result, None)
            if not style_node:
                from writing_bot.graph_schema import StyleElement
                style_node = StyleElement(id=style_id, name=style, count=1)
                style_node = db.save_node(style_node)
            else:
                # Increment count
                current_count = style_node['n'].get('count', 0)
                db.execute(
                    "MATCH (n:StyleElement {id: $id}) SET n.count = $count",
                    {"id": style_id, "count": current_count + 1}
                )
                from writing_bot.graph_schema import StyleElement
                style_node = StyleElement(**style_node['n'])
                style_node.count = current_count + 1
            rel = Relationship(type="HAS_STYLE", start_node_id=article_node._id, end_node_id=style_node._id)
            db.save_relationship(rel)
        # Add ProcessStep nodes and relationships
        for step in process_steps:
            step_id = f"process_{step}"
            result = db.execute_and_fetch(
                "MATCH (n:ProcessStep {id: $id}) RETURN n",
                {"id": step_id}
            )
            process_node = next(result, None)
            if not process_node:
                from writing_bot.graph_schema import ProcessStep
                process_node = ProcessStep(id=step_id, name=step, count=1)
                process_node = db.save_node(process_node)
            else:
                current_count = process_node['n'].get('count', 0)
                db.execute(
                    "MATCH (n:ProcessStep {id: $id}) SET n.count = $count",
                    {"id": step_id, "count": current_count + 1}
                )
                from writing_bot.graph_schema import ProcessStep
                process_node = ProcessStep(**process_node['n'])
                process_node.count = current_count + 1
            rel = Relationship(type="HAS_PROCESS_STEP", start_node_id=article_node._id, end_node_id=process_node._id)
            db.save_relationship(rel) 
