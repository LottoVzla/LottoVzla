from sqlalchemy.orm import Session
import bcrypt
from database import engine, Base, SessionLocal
import models

# Lista oficial de animales de LottoActivo
ANIMALITOS = [
    ("0", "Delfín"), ("00", "Ballena"),
    ("1", "Carnero"), ("2", "Toro"), ("3", "Ciempiés"), ("4", "Alacrán"), ("5", "León"), 
    ("6", "Rana"), ("7", "Perico"), ("8", "Ratón"), ("9", "Águila"), ("10", "Tigre"),
    ("11", "Gato"), ("12", "Caballo"), ("13", "Mono"), ("14", "Paloma"), ("15", "Zorro"), 
    ("16", "Oso"), ("17", "Pavo"), ("18", "Burro"), ("19", "Chivo"), ("20", "Cerdo"),
    ("21", "Gallo"), ("22", "Camello"), ("23", "Cebra"), ("24", "Iguana"), ("25", "Gallina"), 
    ("26", "Vaca"), ("27", "Perro"), ("28", "Zamuro"), ("29", "Elefante"), ("30", "Caimán"),
    ("31", "Lapa"), ("32", "Ardilla"), ("33", "Pescado"), ("34", "Venado"), ("35", "Jirafa"), 
    ("36", "Culebra")
]

def seed_db():
    # Crear tablas en SQLite
    print("Creando base de datos y tablas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Crear usuario Admin
    admin_email = "OrdexAdmin" # Usaremos el username en el campo email para loguearse
    admin_pass = "Vargas05*08?#?"
    
    existing_admin = db.query(models.User).filter(models.User.email == admin_email).first()
    if not existing_admin:
        print(f"Creando usuario administrador: {admin_email}...")
        hashed_pw = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_user = models.User(
            email=admin_email,
            full_name="Administrador Principal",
            hashed_password=hashed_pw,
            is_admin=True
        )
        db.add(admin_user)
    else:
        print("El usuario administrador ya existe. Actualizando contraseña...")
        existing_admin.hashed_password = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 2. Insertar Animalitos
    print("Verificando catálogo de los 38 animalitos de LottoActivo...")
    for number, name in ANIMALITOS:
        existing_animal = db.query(models.Animal).filter(models.Animal.number == number).first()
        if not existing_animal:
            new_animal = models.Animal(number=number, name=name)
            db.add(new_animal)
            print(f"Animal añadido: {number} - {name}")
            
    db.commit()
    db.close()
    print("¡Base de datos sembrada y lista para usarse en producción!")

if __name__ == "__main__":
    seed_db()
