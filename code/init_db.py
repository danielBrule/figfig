from db.database import engine
from db.models import Base

# Create all tables defined in Base metadata
if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created.")
