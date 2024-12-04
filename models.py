from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Song(Base):
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    album = Column(String)
    artist = Column(String)
    spotify_url = Column(String)
    preview_url = Column(String)
    emotion = Column(String)  # ['ANGRY', 'HAPPY', 'SAD', etc.]

# Database connection
DATABASE_URL = "postgresql://username:password@localhost:5432/emotune"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine) 