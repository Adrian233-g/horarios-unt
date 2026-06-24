import sys
import os
from database import engine
from models import Base
import seed_data

def reset():
    print("Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        print(f"Error dropping tables: {e}")
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Running seed...")
    seed_data.run()

if __name__ == "__main__":
    reset()
