import base64
import os

from app.config import settings
from cryptography.fernet import Fernet


# Generate or load encryption key (in production, use AWS KMS or similar)
def get_encryption_key():
    """Get AES-256 encryption key from environment or generate new one"""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Generate new key (store this securely in production!)
        key = Fernet.generate_key()
        print(f"Generated new encryption key: {key.decode()}")
    else:
        key = key.encode()
    return key


# Initialize encryption
encryption_key = get_encryption_key()
cipher_suite = Fernet(encryption_key)


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data using AES-256"""
    if not data:
        return data

    encrypted_data = cipher_suite.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return encrypted_data

    try:
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = cipher_suite.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception:
        # Return original if decryption fails (for backward compatibility)
        return encrypted_data


def encrypt_spec_json(spec_json: dict) -> dict:
    """Encrypt sensitive fields in spec JSON"""
    if not spec_json:
        return spec_json

    # Create a copy to avoid modifying original
    encrypted_spec = spec_json.copy()

    # Encrypt sensitive fields (customize based on your needs)
    sensitive_fields = ["user_notes", "private_data", "personal_info"]

    for field in sensitive_fields:
        if field in encrypted_spec:
            encrypted_spec[field] = encrypt_data(str(encrypted_spec[field]))

    return encrypted_spec


def decrypt_spec_json(encrypted_spec: dict) -> dict:
    """Decrypt sensitive fields in spec JSON"""
    if not encrypted_spec:
        return encrypted_spec

    decrypted_spec = encrypted_spec.copy()

    sensitive_fields = ["user_notes", "private_data", "personal_info"]

    for field in sensitive_fields:
        if field in decrypted_spec:
            decrypted_spec[field] = decrypt_data(decrypted_spec[field])

    return decrypted_spec


# Role-based access control
class Roles:
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


def check_project_access(user_id: str, project_id: str, required_role: str = Roles.USER) -> bool:
    """Check if user has access to project (implement your logic)"""
    # Placeholder - implement based on your project access rules
    if user_id == "admin":
        return True

    # Add your project access logic here
    # e.g., check project_members table, user roles, etc.
    return True


def check_spec_access(user_id: str, spec_owner_id: str, required_role: str = Roles.USER) -> bool:
    """Check if user can access a specific spec"""
    if user_id == "admin":
        return True

    if user_id == spec_owner_id:
        return True

    # Add shared project logic here
    return False
