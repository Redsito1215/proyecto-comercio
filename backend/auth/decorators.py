from functools import wraps

from flask import current_app, g, request

from backend.common.errors import ApiError


def require_permission(permission: str):
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if get_development_bypass():
                g.actor_id = request.headers.get("X-Actor-Id", "development-user")
                return function(*args, **kwargs)
            from backend.db import get_db
            from backend.modules.security.services import authenticate, permissions_for
            raw=request.headers.get("Authorization","").removeprefix("Bearer ").strip();db=get_db();user=authenticate(db,raw)
            if not user:raise ApiError("Autenticación requerida",401,"authentication_required")
            permissions=permissions_for(db,user)
            if permission=="authenticated" or "*" in permissions or permission in permissions:
                g.actor_id=str(user["_id"]);g.user=user
                return function(*args,**kwargs)
            raise ApiError("No tiene permiso para esta operación", 403, "forbidden")
        return wrapped
    return decorator


def get_development_bypass() -> bool:
    return bool(current_app.testing)
