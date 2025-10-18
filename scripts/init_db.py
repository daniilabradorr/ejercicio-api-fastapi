# para iniciar la base de datos
#los imports
from app.database import Base, engine
from app import models 

def main():
    Base.metadata.create_all(bind=engine)
    print("DB creada correctamente")

if __name__ == "__main__":
    main()
