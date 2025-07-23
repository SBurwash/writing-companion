from gqlalchemy import Memgraph, Node, Field, Relationship
from typing import Optional


db = Memgraph()
db.execute("RETURN 1")
print("Successfully connected to Memgraph!")

class Article(Node):
    id: str = Field(index=True, unique=True, db=db)
    title: str = Field(db=db)
    path: str = Field(db=db)  # Path to the article markdown file
    created_at: Optional[str] = Field(default=None, db=db)

class Outline(Node):
    id: str = Field(index=True, unique=True, db=db)
    article_id: str = Field(db=db)  # Link to Article
    path: str = Field(db=db)  # Path to the outline markdown file

class StyleElement(Node):
    id: str = Field(index=True, unique=True, db=db)
    name: str = Field(db=db)
    description: Optional[str] = Field(default=None, db=db)

class ProcessStep(Node):
    id: str = Field(index=True, unique=True, db=db)
    name: str = Field(db=db)
    description: Optional[str] = Field(default=None, db=db)

class Reference(Node):
    id: str = Field(index=True, unique=True, db=db)
    url: str = Field(db=db)
    description: Optional[str] = Field(default=None, db=db)

class HasOutline(Relationship, type="HAS_OUTLINE", db=db):
    pass