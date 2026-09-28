import secrets

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
)

from .config import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
)


security = HTTPBasic()


def require_admin(
    credentials: HTTPBasicCredentials = Depends(security)
):
    username_valid = secrets.compare_digest(
        credentials.username,
        ADMIN_USERNAME
    )

    password_valid = secrets.compare_digest(
        credentials.password,
        ADMIN_PASSWORD
    )

    if not (
        username_valid
        and password_valid
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={
                "WWW-Authenticate": "Basic"
            }
        )

    return credentials.username