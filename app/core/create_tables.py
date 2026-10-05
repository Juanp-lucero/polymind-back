from app.core.database import Base, engine
from app.models.user import User


print("Creando tablas...")

Base.metadata.create_all(bind=engine)

print("✅ Tablas creadas correctamente")