#Los imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

#la url la dejo muy similar al profesor ya que me gusto su modularizacion de los archivos
DATABASE_URL = "sqlite:///./dev.db"

#creo el engine de la BBDD
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


#Inicio la sesion con la configuracion de los commits y que no empuje los cambios a la db ates de cada consulta
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

#la clase declarativa
class Base(DeclarativeBase):
    pass

#creo una sesion por peticion y la cierro automarticamnet al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()