import os
from typing import List, Dict

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), 'articles')


def find_article_projects() -> List[Dict]:
    """
    Scan the articles directory for subfolders containing outline.md and article.md.
    Returns a list of dicts with paths and basic metadata.
    """
    projects = []
    for entry in os.listdir(ARTICLES_DIR):
        subdir = os.path.join(ARTICLES_DIR, entry)
        if os.path.isdir(subdir):
            outline_path = os.path.join(subdir, 'outline.md')
            article_path = os.path.join(subdir, 'article.md')
            if os.path.exists(outline_path) and os.path.exists(article_path):
                projects.append({
                    'name': entry,
                    'outline_path': outline_path,
                    'article_path': article_path
                })
    return projects


def read_markdown_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read() 