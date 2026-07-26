import chromadb
from pathlib import Path

p = Path('backend/vector_db')
client = chromadb.PersistentClient(path=str(p))
try:
    client.delete_collection('documents')
    print('deleted')
except Exception as e:
    print('delete-error', e)
col = client.get_or_create_collection('documents')
print('created', col)
