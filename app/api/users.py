from fastapi import APIRouter, Depends

from .. import models, schemas
from ..auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user
