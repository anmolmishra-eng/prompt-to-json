"""
Complete Database Connection Management
Session handling, connection pooling, health checks
"""
import logging
import time
from contextlib import contextmanager
from typing import Generator

from app.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

logger = logging.getLogger(__name__)

# ============================================================================
# ENGINE CONFIGURATION
# ============================================================================

# Choose pool and engine args based on database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine_kwargs = {
        "poolclass": NullPool,
        "connect_args": {"check_same_thread": False},
        "echo": settings.DB_ECHO,
        "future": True,
    }
else:
    # PostgreSQL configuration
    poolclass = QueuePool if settings.ENVIRONMENT == "production" else NullPool
    engine_kwargs = {
        "poolclass": poolclass,
        "echo": settings.DB_ECHO,
        "echo_pool": False,
        "future": True,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": f"bhiv-{settings.ENVIRONMENT}",
            "options": "-c timezone=utc",
        },
    }

    # Add pooling parameters only for pooled connections
    if poolclass == QueuePool:
        engine_kwargs.update(
            {
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "pool_recycle": settings.DB_POOL_RECYCLE,
                "pool_pre_ping": True,
            }
        )

# Create engine with appropriate configuration
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# ============================================================================
# SESSION CONFIGURATION
# ============================================================================

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# Base class for models
Base = declarative_base()

# ============================================================================
# FASTAPI DEPENDENCY
# ============================================================================


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions

    Usage:
        @router.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            # Use db here

    Automatically handles:
    - Session creation
    - Commit on success
    - Rollback on error
    - Session cleanup
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


# ============================================================================
# CONTEXT MANAGER
# ============================================================================


@contextmanager
def get_db_context():
    """
    Context manager for database sessions outside FastAPI

    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
            # Auto-commits on exit
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database context error: {e}")
        raise
    finally:
        db.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================


def create_test_user():
    """
    Create test user for API testing
    """
    try:
        from app.models import User

        with get_db_context() as db:
            # Check if test user already exists
            existing_user = db.query(User).filter(User.username == "test_user").first()
            if existing_user:
                return

            # Create test user
            test_user = User(
                id="test_user",
                username="test_user",
                email="test@example.com",
                password_hash="dummy_hash",
                full_name="Test User",
                is_active=True,
            )
            db.add(test_user)
            db.commit()
            logger.info("Test user created successfully")
    except Exception as e:
        logger.warning(f"Failed to create test user: {e}")


def init_db():
    """
    Initialize database tables
    Call this on application startup

    Creates all tables defined in models.py
    """
    try:
        # Import models to register them
        # Create tables in dependency order
        from app.models import AuditLog
        from app.models import Base as ModelsBase
        from app.models import ComplianceCheck, Evaluation, Iteration, RefreshToken, RLFeedback, Spec, User, WorkflowRun

        # Drop and recreate if in development
        if settings.ENVIRONMENT == "development":
            try:
                ModelsBase.metadata.drop_all(bind=engine)
            except Exception as drop_error:
                logger.warning(f"Drop tables warning: {drop_error}")
                # Try CASCADE drop for PostgreSQL
                if not settings.DATABASE_URL.startswith("sqlite"):
                    with engine.connect() as conn:
                        conn.execute(text("DROP SCHEMA public CASCADE"))
                        conn.execute(text("CREATE SCHEMA public"))
                        conn.commit()

        ModelsBase.metadata.create_all(bind=engine)

        # Create test user for API testing
        create_test_user()

        logger.info("Database tables initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def drop_all_tables():
    """
    Drop all database tables
    ⚠️  DANGEROUS - Use only in development/testing
    """
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot drop tables in production!")

    from app.models import Base as ModelsBase

    ModelsBase.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


# ============================================================================
# HEALTH CHECKS
# ============================================================================


def check_db_connection() -> dict:
    """
    Comprehensive database health check

    Returns:
        dict with status, latency, pool stats
    """
    start_time = time.time()

    try:
        with engine.connect() as conn:
            # Simple query
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

            # Get pool stats (if using pooling)
            pool_stats = {}
            if hasattr(engine.pool, "size"):
                pool = engine.pool
                pool_stats = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "max_overflow": settings.DB_MAX_OVERFLOW,
                }
            else:
                pool_stats = {"type": "no_pooling"}

            latency_ms = (time.time() - start_time) * 1000

            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "pool": pool_stats,
                "database": "configured",
            }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "error": str(e), "latency_ms": round((time.time() - start_time) * 1000, 2)}


def get_db_stats() -> dict:
    """
    Get detailed database statistics
    """
    try:
        with engine.connect() as conn:
            if settings.DATABASE_URL.startswith("sqlite"):
                # SQLite stats
                tables_query = text(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """
                )
                tables = conn.execute(tables_query).fetchall()

                return {
                    "database_type": "sqlite",
                    "tables": [{"name": t[0]} for t in tables],
                    "operations": "not_available_in_sqlite",
                }
            else:
                # PostgreSQL stats
                size_query = text(
                    """
                    SELECT
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """
                )

                tables = conn.execute(size_query).fetchall()

                # Get row counts
                count_query = text(
                    """
                    SELECT
                        schemaname,
                        relname as tablename,
                        n_tup_ins AS inserts,
                        n_tup_upd AS updates,
                        n_tup_del AS deletes
                    FROM pg_stat_user_tables
                    WHERE schemaname = 'public'
                """
                )

                stats = conn.execute(count_query).fetchall()

                return {
                    "database_type": "postgresql",
                    "tables": [{"schema": r[0], "table": r[1], "size": r[2]} for r in tables],
                    "operations": [
                        {"schema": r[0], "table": r[1], "inserts": r[2], "updates": r[3], "deletes": r[4]}
                        for r in stats
                    ],
                }
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {"error": str(e)}


# ============================================================================
# EVENT LISTENERS
# ============================================================================


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """
    Called when a new connection is created
    Set up session-level configuration
    """
    if not settings.DATABASE_URL.startswith("sqlite"):
        # PostgreSQL specific settings
        with dbapi_conn.cursor() as cursor:
            # Set timezone to UTC
            cursor.execute("SET timezone='UTC'")
            # Set statement timeout (30 seconds)
            cursor.execute("SET statement_timeout = 30000")

    logger.debug("New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Called when a connection is retrieved from the pool"""
    logger.debug("Connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Called when a connection is returned to the pool"""
    logger.debug("Connection returned to pool")


# ============================================================================
# UTILITIES
# ============================================================================


def reset_database():
    """
    Reset database (drop + recreate)
    ⚠️  DANGEROUS - Development only
    """
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot reset database in production!")

    drop_all_tables()
    init_db()
    logger.info("Database reset complete")


# ============================================================================
# STARTUP CHECKS
# ============================================================================


def validate_database():
    """
    Validate database configuration on startup
    """
    logger.info("Validating database configuration...")

    # Check connection
    health = check_db_connection()
    if health["status"] != "healthy":
        raise RuntimeError(f"Database connection failed: {health.get('error', 'Unknown error')}")

    logger.info(f"Database connected (latency: {health['latency_ms']}ms)")
    if "size" in health["pool"]:
        logger.info(f"Pool size: {health['pool']['size']} (checked out: {health['pool']['checked_out']})")


# Run validation on import (only if not in test mode)
if __name__ != "__main__" and not settings.DATABASE_URL.startswith("sqlite:///:memory:"):
    try:
        validate_database()
    except Exception as e:
        logger.error(f"Database validation failed: {e}")

# ============================================================================
# AUTHENTICATION DEPENDENCY
# ============================================================================


def get_current_user(token: str = Depends(HTTPBearer())) -> str:
    """
    JWT authentication dependency
    Validates JWT tokens and returns current user
    """
    try:
        import jwt
        from app.config import settings

        # Extract token from Bearer scheme
        token_str = token.credentials

        # Decode and validate JWT token
        payload = jwt.decode(token_str, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return username

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Export commonly used items
__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "get_db_context",
    "init_db",
    "check_db_connection",
    "get_current_user",
]
