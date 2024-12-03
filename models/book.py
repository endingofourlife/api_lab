from typing import Optional

from pydantic import BaseModel, Field


class BookRequest(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=10, max_length=100)
    rating: int = Field(gt=0, lt=5)

class BookModel:
    def __init__(self, id: int, title: str, author: str, description: str, rating: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

    id: int
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=10, max_length=100)
    rating: int = Field(gt=0, lt=5)
