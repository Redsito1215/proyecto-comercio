from functools import wraps

from flask import g, request

from backend.common.errors import ApiError


def require_permission(permission: str):
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            # En desarrollo permite cabeceras explícitas; 007 sustituirá esto por sesión segura.
            permissions = {item.strip() for item in request.headers.get("X-Permissions", "").split(",") if item.strip()}
            if get_development_bypass() or permission in permissions:
                g.actor_id = request.headers.get("X-Actor-Id", "development-user")
                return function(*args, **kwargs)
            raise ApiError("No tiene permiso para esta operación", 403, "forbidden")
        return wrapped
    return decorator


def get_development_bypass() -> bool:
    from backend.config import get_settings
    return get_settings().app_env == "development"
