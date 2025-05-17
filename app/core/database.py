from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Connection string
SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://devuser:Awst0azure_260824@frc-sh-int-db01.database.windows.net/Shiptech-TNT-Dev?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 