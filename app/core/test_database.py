from app.core.database import engine


try:
    connection = engine.connect()
    print("✅ Conexión con PostgreSQL exitosa")
    connection.close()
except Exception as e:
    print("❌ Error de conexión:")
    print(e)