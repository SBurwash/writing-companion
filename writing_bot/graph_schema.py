from gqlalchemy import Memgraph, Node, Field, Relationship
from typing import Optional


db = Memgraph()
db.execute("RETURN 1")
print("Successfully connected to Memgraph!")

class Article(Node):
    id: str = Field(index=True, unique=True)
    title: str = Field()
    path: str = Field()  # Path to the article markdown file
    created_at: Optional[str] = Field(default=None)

class Outline(Node):
    id: str = Field(index=True, unique=True)
    article_id: str = Field()  # Link to Article
    path: str = Field()  # Path to the outline markdown file

class StyleElement(Node):
    id: str = Field(index=True, unique=True)
    name: str = Field()
    count: int = Field(default=0)
    description: Optional[str] = Field(default=None)

class ProcessStep(Node):
    id: str = Field(index=True, unique=True)
    name: str = Field()
    count: int = Field(default=0)
    description: Optional[str] = Field(default=None)

class Reference(Node):
    id: str = Field(index=True, unique=True)
    url: str = Field()
    description: Optional[str] = Field(default=None)

class HasOutline(Relationship, type="HAS_OUTLINE", db=db):
    pass