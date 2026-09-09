import time
import base64
import jwt
import httpx
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dataclasses import dataclass
from config import SUPABASE_JWT_SECRET, SUPABASE_URL

security = HTTPBearer()

_jwks_cache = None
_jwks_cache_time = 0.0
JWKS_TTL = 600.0


@dataclass
class AuthenticatedUser:
    user_id: str
    email: str
    role: str


def _b64_to_int(value: str) -> int:
    pad = "=" * (-len(value) % 4)
    return int.from_bytes(base64.urlsafe_b64decode(value + pad), "big")


def _jwk_to_key(jwk: dict):
    if jwk.get("kty") == "EC":
        return ec.EllipticCurvePublicNumbers(
            _b64_to_int(jwk["x"]), _b64_to_int(jwk["y"]), ec.SECP256R1()
        ).public_key()
    if jwk.get("kty") == "RSA":
        return rsa.RSAPublicNumbers(
            _b64_to_int(jwk["n"]), _b64_to_int(jwk["e"])
        ).public_key()
    raise jwt.InvalidTokenError("Unsupported key type")


def _get_jwks():
    global _jwks_cache, _jwks_cache_time
    now = time.time()
    if _jwks_cache is None or (now - _jwks_cache_time) > JWKS_TTL:
        resp = httpx.get(
            f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json",
            timeout=15.0,
        )
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_cache_time = now
    return _jwks_cache


def _verify_with_jwks(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    jwks = _get_jwks()
    jwk = None
    for k in jwks.get("keys", []):
        if k.get("kid") == header.get("kid"):
            jwk = k
            break
    if jwk is None:
        raise jwt.InvalidTokenError("Matching key not found")

    key = _jwk_to_key(jwk)

    try:
        return jwt.decode(
            token,
            key,
            algorithms=["ES256", "RS256", "HS256"],
            audience="authenticated",
        )
    except jwt.InvalidTokenError:
        # Retry once after refreshing cache (key rotation)
        global _jwks_cache, _jwks_cache_time
        _jwks_cache = None
        jwks = _get_jwks()
        for k in jwks.get("keys", []):
            if k.get("kid") == header.get("kid"):
                jwk = k
                break
        if jwk is None:
            raise jwt.InvalidTokenError("Matching key not found")
        return jwt.decode(
            token,
            _jwk_to_key(jwk),
            algorithms=["ES256", "RS256", "HS256"],
            audience="authenticated",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthenticatedUser:
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "")

        if alg == "HS256" and SUPABASE_JWT_SECRET and SUPABASE_JWT_SECRET != "your_jwt_secret_here":
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
            return AuthenticatedUser(
                user_id=payload["sub"],
                email=payload.get("email", ""),
                role=payload.get("role", "authenticated"),
            )

        payload = _verify_with_jwks(token)
        return AuthenticatedUser(
            user_id=payload["sub"],
            email=payload.get("email", ""),
            role=payload.get("role", "authenticated"),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except (jwt.InvalidTokenError, httpx.HTTPError) as exc:
        # Fallback: let Supabase verify the token server-side
        from database import get_admin_client
        try:
            admin = get_admin_client()
            result = admin.auth.get_user(token)
            user = result.user
            return AuthenticatedUser(
                user_id=user.id,
                email=user.email or "",
                role="authenticated",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )


def require_role(allowed_roles: list[str]):
    async def checker(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return checker