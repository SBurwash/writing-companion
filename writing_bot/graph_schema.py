from gqlalchemy import Memgraph, Node, Field
from typing import Optional

class Article(Node):
    id: str
    title: str
    path: str  # Path to the article markdown file
    created_at: Optional[str]

class Outline(Node):
    id: str
    article_id: str  # Link to Article
    path: str  # Path to the outline markdown file

class StyleElement(Node):
    id: str
    name: str
    description: Optional[str]

class ProcessStep(Node):
    id: str
    name: str
    description: Optional[str]

class Reference(Node):
    id: str
    url: str
    description: Optional[str] 