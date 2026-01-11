from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    role: str
    email: str = Field(index=True, unique=True)
    hash_pass: str
    
class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    pdf_name: str
    pdf_path: str

    excel_name: str
    excel_path: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
