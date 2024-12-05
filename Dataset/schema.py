"""
dataset schema
"""

from pydantic import BaseModel, Field
from typing import Dict, Literal, Union, List



class Annotation(BaseModel):
    lyrics: str
    annotation: str
    source: str


class Song(BaseModel):
    name: str
    content: List[Annotation]
    lyrics_source: str



class Gpt_response(BaseModel):
    entity: str
    type: Literal["person", "group", "artwork", "event", "place", "phrase", "brand"]
    description: str



class Entity(BaseModel):
    name: str
    type: Literal["person", "group", "artwork", "event", "place", "phrase", "brand"]
    id: str



class Edge(BaseModel):
    name: Literal["reference", "creation"]
    source_entity_id: str
    target_entity_id: str
    id: str
    description: str
    info_source: str

    

class Namespace(BaseModel):
    name_to_id: Dict[str, str] = Field(default_factory=dict)
    id_to_name: Dict[str, str] = Field(default_factory=dict)
    entities: List[Entity] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    id_to_object: Dict[str, Union[Entity, Edge]] = Field(default_factory=dict)
