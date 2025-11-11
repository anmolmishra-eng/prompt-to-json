import ssl

import uvicorn
from app.main import app


# HTTPS configuration for production
def run_with_https():
    """Run server with HTTPS/TLS support"""

    # SSL context for HTTPS
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # In production, use real certificates
    # ssl_context.load_cert_chain("path/to/cert.pem", "path/to/key.pem")

    # For development, create self-signed cert:
    # openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443,  # HTTPS port
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
        ssl_version=ssl.PROTOCOL_TLS_SERVER,
    )


if __name__ == "__main__":
    run_with_https()
