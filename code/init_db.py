from sqlalchemy.orm import Session

from db.database import engine
from db.models import Base, Newspaper
from utils.constants import NewspaperEnum

def create_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created.")


def init_tables():
    l_data = []
    for member in NewspaperEnum:
        l_data.append(Newspaper(id= member.value, name=member.name))
    with Session(engine) as session:
        session.add_all(l_data)
        session.commit()
            

# Create all tables defined in Base metadata
if __name__ == "__main__":
    create_tables()
    init_tables()