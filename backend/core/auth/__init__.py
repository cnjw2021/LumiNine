"""Authentication module initialization."""

from .auth_routes import auth_bp, create_auth_bp

__all__ = ['auth_bp', 'create_auth_bp']
