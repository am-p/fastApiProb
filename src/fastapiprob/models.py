from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    role: str
    email: str
    hash_pass: str
    
class PdfInvoice(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    created_at: datetime=Field(default_factory=datetime.utcnow)

class ExcelFromInvoice(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    pdf_id: int= Field(foreign_key="pdfinvoice.id", unique=True)
    created_at: datetime=Field(default_factory=datetime.utcnow)
    
        
