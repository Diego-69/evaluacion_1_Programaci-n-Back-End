"""Configuración de la base de datos.

Este módulo centraliza la creación del `engine`, la fábrica de sesiones (`SessionLocal`) y la
clase base declarativa (`Base`) que utilizarán los modelos ORM. Se expone además el
*dependency* `get_db` que FastAPI inyectará en los endpoints para disponer de una sesión
por petición y garantizar su cierre correcto.

Usamos SQLite para simplificar la evaluación (archivo local `app.db`). Para evitar el error
"SQLite objects created in a thread…" activamos `check_same_thread=False` ya que FastAPI
maneja peticiones concurrentes.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexión. Para un archivo local basta con la ruta relativa.
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Engine de SQLAlchemy. `connect_args` es específico de SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Activar enforcement de claves foráneas en SQLite en cada conexión
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        # En caso de motores no SQLite, ignorar silenciosamente
        pass

# Fábrica de sesiones: sin autocommit y sin autoflush para tener control explícito.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base que heredarán todos los modelos ORM.
Base = declarative_base()

def get_db():
    """
    Dependency de FastAPI que proporciona una sesión de base de datos.

    Se crea una sesión al entrar y se garantiza su cierre al terminar la petición.
    """
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
