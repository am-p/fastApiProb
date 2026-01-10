from sqlmodel import SQLModel, Session
from fastapiprob.database import engine
from fastapiprob.models import User

SQLModel.metadata.create_all(engine)


with Session(engine) as session:
    session.add(User(
        name="Zunilda",
        role="user",
        email="zunigonz@gmail.com",
        hash_pass="hashed_here"
        ))
    session.add(User(
        name="Miriam",
        role="user",
        email="miruorellana@gmail.com",
        hash_pass="hashed_here"
        ))
    session.commit()
