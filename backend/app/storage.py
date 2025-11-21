import logging
import uuid
from typing import Optional

from app.config import settings
from supabase import Client, create_client

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


async def upload_to_bucket(bucket: str, path: str, data: bytes) -> dict:
    """Upload file to Supabase bucket"""
    try:
        result = supabase.storage.from_(bucket).upload(path, data)
        logger.info(f"Uploaded to {bucket}/{path}")
        return result
    except Exception as e:
        logger.error(f"Upload failed: {e}")

        # Check if it's a bucket not found error
        if "Bucket not found" in str(e):
            raise Exception(
                f"Supabase bucket '{bucket}' not found. "
                f"Please create the bucket in your Supabase dashboard: "
                f"https://supabase.com/dashboard -> Storage -> Create bucket '{bucket}'"
            )

        raise Exception(f"Upload to {bucket}/{path} failed: {e}")


async def get_signed_url(bucket: str, path: str, expires: int = 600) -> str:
    """Get signed URL for secure file access"""
    try:
        resp = supabase.storage.from_(bucket).create_signed_url(path, expires)
        signed_url = resp.get("signedURL")
        logger.info(f"Generated signed URL for {bucket}/{path}, expires in {expires}s")
        return signed_url
    except Exception as e:
        logger.error(f"Signed URL generation failed: {e}")
        raise Exception(f"Failed to generate signed URL for {bucket}/{path}: {e}")


# Bucket-specific upload functions
async def upload_preview(spec_id: str, preview_bytes: bytes) -> str:
    """Upload preview GLB file"""
    path = f"{spec_id}.glb"
    await upload_to_bucket("previews", path, preview_bytes)
    return await get_signed_url("previews", path, expires=600)


async def upload_geometry(spec_id: str, geometry_bytes: bytes, file_type: str = "stl") -> str:
    """Upload geometry STL file"""
    path = f"{spec_id}.{file_type}"
    await upload_to_bucket("geometry", path, geometry_bytes)
    return await get_signed_url("geometry", path, expires=600)


async def upload_compliance(case_id: str, compliance_bytes: bytes) -> str:
    """Upload compliance ZIP file"""
    path = f"{case_id}.zip"
    await upload_to_bucket("compliance", path, compliance_bytes)
    return await get_signed_url("compliance", path, expires=600)


class StorageManager:
    def __init__(self):
        self.client = supabase
        self.bucket = settings.SUPABASE_BUCKET

    async def upload_file(self, file_content: bytes, filename: str) -> str:
        """Upload file and return file path"""
        file_id = str(uuid.uuid4())
        file_path = f"{file_id}_{filename}"

        await upload_to_bucket(self.bucket, file_path, file_content)
        return file_path

    async def get_signed_url(self, file_path: str, expires_in: int = 600) -> str:
        """Generate signed URL for file access"""
        return await get_signed_url(self.bucket, file_path, expires_in)


storage_manager = StorageManager()
