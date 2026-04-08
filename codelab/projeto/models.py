from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class ExtensionGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    logo_url: str
    website: Optional[str] = Field(default=None)
    
    events: List["Event"] = Relationship(back_populates="group")

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    date: str
    location: str = Field(default="")
    description: str
    group_id: Optional[int] = Field(default=None, foreign_key="extensiongroup.id")
    
    group: Optional[ExtensionGroup] = Relationship(back_populates="events")
