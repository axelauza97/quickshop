import os
import ssl

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from models.db.session import get_session
from services.user_service import get_or_create_authenticated_user


def _auth0_domain() -> str:
    v = os.getenv("AUTH0_DOMAIN")
    if not v:
        raise RuntimeError("Missing AUTH0_DOMAIN environment variable.")
    return v


def _auth0_audience() -> str:
    v = os.getenv("AUTH0_API_AUDIENCE")
    if not v:
        raise RuntimeError("Missing AUTH0_API_AUDIENCE environment variable.")
    return v


def _auth0_issuer() -> str:
    v = os.getenv("AUTH0_ISSUER")
    if not v:
        raise RuntimeError("Missing AUTH0_ISSUER environment variable.")
    return v


PERMISSION_TO_ROLES = {
    "read:category": {"admin"},
    "create:category": {"admin"},
    "update:category": {"admin"},
    "delete:category": {"admin"},
    "read:product": {"admin"},
    "create:product": {"admin"},
    "update:product": {"admin"},
    "delete:product": {"admin"},
    "read:order": {"admin", "customer"},
    "create:order": {"admin", "customer"},
    "update:order": {"admin"},
    "delete:order": {"admin"},
    "read:order_item": {"admin"},
    "create:order_item": {"admin"},
    "update:order_item": {"admin"},
    "delete:order_item": {"admin"},
    "read:user": {"admin", "customer"},
    "update:user": {"admin"},
    "delete:user": {"admin"},
    "read:cart": {"admin", "customer"},
    "create:cart": {"admin", "customer"},
    "update:cart": {"admin", "customer"},
    "delete:cart": {"admin", "customer"},
    "create:checkout": {"admin", "customer"},
}


security = HTTPBearer()

def _jwks_ssl_context() -> ssl.SSLContext:
    if os.getenv("AUTH0_SKIP_TLS_VERIFY", "").strip().lower() == "true":
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    ca_cert_path = os.getenv("AUTH0_CA_CERT_PATH")
    if ca_cert_path:
        return ssl.create_default_context(cafile=ca_cert_path)

    return ssl.create_default_context()


def _extract_roles(payload: dict) -> list[str]:
    domain = _auth0_domain()
    audience = _auth0_audience()
    roles = (
        payload.get("roles")
        or payload.get(f"https://{domain}/roles")
        or payload.get(f"{audience}/roles")
        or []
    )
    if isinstance(roles, str):
        roles = [roles]
    return [role for role in roles if isinstance(role, str)]


def _decode_token(token: str) -> dict:
    domain = _auth0_domain()
    jwks_client = jwt.PyJWKClient(
        f"https://{domain}/.well-known/jwks.json",
        ssl_context=_jwks_ssl_context(),
    )
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
    except jwt.PyJWKClientConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to fetch Auth0 JWKS. "
                "Check container TLS trust or configure AUTH0_CA_CERT_PATH."
            ),
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    try:
        return jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=_auth0_audience(),
            issuer=_auth0_issuer(),
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> dict:
    payload = _decode_token(credentials.credentials)
    roles = _extract_roles(payload)
    if not roles:
        raise HTTPException(
            status_code=403,
            detail="No roles found. Add roles to the token via an Auth0 Action.",
        )

    auth0_sub = payload.get("sub")
    if not auth0_sub:
        raise HTTPException(status_code=401, detail="Invalid token: missing subject")

    return get_or_create_authenticated_user(session, auth0_sub, roles)


def require_permission(permission: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] == "admin":
            return user

        allowed_roles = PERMISSION_TO_ROLES.get(permission, set())
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return checker
