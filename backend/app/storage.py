"""
Storage Module - Supabase Storage Integration
Handles file uploads, previews, and signed URLs
"""
import logging
import mimetypes
from typing import Optional

from app.config import settings
from supabase import Client, create_client

logger = logging.getLogger(__name__)

# Bucket name mapping to handle case sensitivity
BUCKET_MAPPING = {
    "files": "Files",  # Handle case mismatch
    "previews": "previews",
    "geometry": "geometry",
    "compliance": "compliance",
}


def get_bucket_name(bucket: str) -> str:
    """Get actual bucket name handling case variations"""
    return BUCKET_MAPPING.get(bucket, bucket)


# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Service role client for admin operations
try:
    service_key = getattr(settings, "SUPABASE_SERVICE_KEY", None)
    if service_key:
        supabase_admin: Client = create_client(settings.SUPABASE_URL, service_key)
    else:
        supabase_admin = supabase
except:
    supabase_admin = supabase

# ============================================================================
# BUCKET MANAGEMENT
# ============================================================================


def ensure_buckets_exist():
    """
    Ensure all required storage buckets exist
    Creates them if they don't exist
    """
    required_buckets = [
        settings.STORAGE_BUCKET_FILES,
        settings.STORAGE_BUCKET_PREVIEWS,
        settings.STORAGE_BUCKET_GEOMETRY,
        settings.STORAGE_BUCKET_COMPLIANCE,
    ]

    try:
        # Get existing buckets using admin client
        existing = supabase_admin.storage.list_buckets()
        existing_names = [b.name for b in existing] if hasattr(existing, "__iter__") else []

        # Create missing buckets
        for bucket in required_buckets:
            if bucket not in existing_names:
                try:
                    supabase_admin.storage.create_bucket(bucket, options={"public": False})
                    logger.info(f"Created bucket: {bucket}")
                except Exception as bucket_error:
                    # Handle RLS policy errors gracefully
                    if "row-level security" in str(bucket_error).lower() or "403" in str(bucket_error):
                        logger.warning(f"Bucket {bucket} creation blocked by RLS policy - may already exist")
                    else:
                        logger.error(f"Failed to create bucket {bucket}: {bucket_error}")
            else:
                logger.info(f"Bucket exists: {bucket}")

        return True

    except Exception as e:
        logger.warning(f"Bucket check failed (non-critical): {e}")
        return True  # Return True to continue startup


# ============================================================================
# FILE UPLOAD
# ============================================================================


def upload_file(file_path: str, bucket: str, destination_path: str, content_type: Optional[str] = None) -> str:
    """
    Upload file to Supabase storage

    Args:
        file_path: Local file path
        bucket: Target bucket name
        destination_path: Path in bucket (e.g., "users/123/file.pdf")
        content_type: MIME type (auto-detected if None)

    Returns:
        Public URL or signed URL
    """
    try:
        # Auto-detect content type
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or "application/octet-stream"

        # Read file
        with open(file_path, "rb") as f:
            file_data = f.read()

        # Upload to Supabase (use mapped bucket name)
        actual_bucket = get_bucket_name(bucket)
        result = supabase.storage.from_(actual_bucket).upload(
            destination_path, file_data, file_options={"content-type": content_type}
        )

        # Get public URL
        url = supabase.storage.from_(actual_bucket).get_public_url(destination_path)

        logger.info(f"Uploaded: {destination_path} to {bucket}")
        return url

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise


def upload_preview(spec_id: str, preview_data: bytes, format: str = "png") -> str:
    """
    Upload design preview image

    Args:
        spec_id: Specification ID
        preview_data: Image bytes
        format: Image format (png, jpg)

    Returns:
        Preview URL
    """
    destination = f"previews/{spec_id}.{format}"

    try:
        actual_bucket = get_bucket_name(settings.STORAGE_BUCKET_PREVIEWS)
        result = supabase.storage.from_(actual_bucket).upload(
            destination, preview_data, file_options={"content-type": f"image/{format}"}
        )

        url = supabase.storage.from_(actual_bucket).get_public_url(destination)

        logger.info(f"Preview uploaded: {spec_id}")
        return url

    except Exception as e:
        logger.error(f"Preview upload failed: {e}")
        raise


def upload_geometry(spec_id: str, glb_data: bytes) -> str:
    """
    Upload .GLB geometry file

    Args:
        spec_id: Specification ID
        glb_data: GLB file bytes

    Returns:
        Geometry URL
    """
    destination = f"geometry/{spec_id}.glb"

    try:
        actual_bucket = get_bucket_name(settings.STORAGE_BUCKET_GEOMETRY)
        result = supabase.storage.from_(actual_bucket).upload(
            destination, glb_data, file_options={"content-type": "model/gltf-binary"}
        )

        url = supabase.storage.from_(actual_bucket).get_public_url(destination)

        logger.info(f"Geometry uploaded: {spec_id}")
        return url

    except Exception as e:
        logger.error(f"Geometry upload failed: {e}")
        raise


# ============================================================================
# SIGNED URLS
# ============================================================================


def generate_signed_url(file_path: str, bucket: Optional[str] = None, expires_in: int = 3600) -> str:
    """
    Generate signed URL for private file access

    Args:
        file_path: Full URL or path in bucket
        bucket: Bucket name (auto-detected if None)
        expires_in: Expiration time in seconds

    Returns:
        Signed URL
    """
    try:
        # If full URL provided, extract path and bucket
        if file_path.startswith("http"):
            # Extract bucket and path from URL
            parts = file_path.split("/storage/v1/object/public/")
            if len(parts) > 1:
                bucket_and_path = parts[1].split("/", 1)
                bucket = bucket_and_path[0]
                file_path = bucket_and_path[1]

        if not bucket:
            raise ValueError("Bucket name required")

        # Generate signed URL (use mapped bucket name)
        actual_bucket = get_bucket_name(bucket)
        signed_url = supabase.storage.from_(actual_bucket).create_signed_url(file_path, expires_in)

        return signed_url["signedURL"]

    except Exception as e:
        logger.error(f"Signed URL generation failed: {e}")
        return file_path  # Return original URL as fallback


# ============================================================================
# FILE MANAGEMENT
# ============================================================================


def delete_file(file_path: str, bucket: str) -> bool:
    """Delete file from storage"""
    try:
        actual_bucket = get_bucket_name(bucket)
        supabase.storage.from_(actual_bucket).remove([file_path])
        logger.info(f"Deleted: {file_path} from {bucket}")
        return True
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        return False


def list_files(bucket: str, path: str = "") -> list:
    """List files in bucket path"""
    try:
        actual_bucket = get_bucket_name(bucket)
        files = supabase.storage.from_(actual_bucket).list(path)
        return files
    except Exception as e:
        logger.error(f"List failed: {e}")
        return []


# ============================================================================
# INITIALIZATION
# ============================================================================


def init_storage():
    """Initialize storage system on startup"""
    logger.info("Initializing Supabase storage...")
    try:
        success = ensure_buckets_exist()
        if success:
            logger.info("Storage initialization complete")
        else:
            logger.info("Storage initialization completed with warnings")
        return success
    except Exception as e:
        logger.info(f"Storage initialization skipped: {e}")
        return True  # Don't block startup


# ============================================================================
# COMPATIBILITY ALIASES
# ============================================================================


def get_signed_url(bucket: str, file_path: str, expires: int = 3600) -> str:
    """Alias for generate_signed_url for backward compatibility"""
    return generate_signed_url(file_path, bucket, expires)


async def upload_to_bucket(bucket: str, file_path: str, data: bytes) -> str:
    """Upload data to bucket (async wrapper)"""
    try:
        actual_bucket = get_bucket_name(bucket)
        result = supabase.storage.from_(actual_bucket).upload(
            file_path, data, file_options={"content-type": "application/octet-stream"}
        )
        url = supabase.storage.from_(actual_bucket).get_public_url(file_path)
        return url
    except Exception as e:
        logger.error(f"Upload to bucket failed: {e}")
        raise


# Skip automatic bucket creation - create manually in Supabase dashboard
# Go to: https://supabase.com/dashboard/project/dntmhjlbxirtgslzwbui/storage/buckets
# Create buckets: files, previews, geometry, compliance
if __name__ != "__main__":
    logger.info("Storage buckets should be created manually in Supabase dashboard")
