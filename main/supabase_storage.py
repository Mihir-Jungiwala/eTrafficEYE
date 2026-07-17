import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from supabase import create_client

# Explicitly load .env from the same folder as this file
BASE_DIR = Path(__file__).resolve().parent
print("Looking for:", BASE_DIR / ".env")
print("Exists:", (BASE_DIR / ".env").exists())

from dotenv import dotenv_values

config = dotenv_values(BASE_DIR / ".env")
print(config)

SUPABASE_URL = config.get("SUPABASE_URL")
SUPABASE_KEY = config.get("SUPABASE_KEY")
SUPABASE_BUCKET = config.get("SUPABASE_BUCKET")

print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_BUCKET:", SUPABASE_BUCKET)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseStorage(Storage):

    def _save(self, name, content):
        content.seek(0)
        data = content.read()

        supabase.storage.from_(SUPABASE_BUCKET).upload(
            name,
            data,
            {"content-type": content.content_type}
        )

        return name

    def exists(self, name):
        return False

    def url(self, name):
        return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(name)

    def delete(self, name):
        supabase.storage.from_(SUPABASE_BUCKET).remove([name])

    def open(self, name, mode='rb'):
        data = supabase.storage.from_(SUPABASE_BUCKET).download(name)
        return ContentFile(data)
    
    