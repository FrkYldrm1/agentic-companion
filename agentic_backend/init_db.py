from memory_layer.models import Base
from memory_layer.db import engine

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Done.")
