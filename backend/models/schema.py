# backend/models/schema.py
# Defines the core data structures used throughout the pipeline.

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ImageMeta:
    page: int
    path: str


@dataclass
class TableMeta:
    page: int
    data: List[List[Any]]


@dataclass
class Chunk:
    id: int
    text: str
    type: str          # "heading" | "content" | "bullet"
    page: int
    heading: Optional[str]
    embedding: Any     # np.ndarray float32
    length: int
    links: List[dict] = field(default_factory=list)
    images: List[ImageMeta] = field(default_factory=list)
    tables: List[TableMeta] = field(default_factory=list)
