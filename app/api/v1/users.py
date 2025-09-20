from fastapi import APIRouter, Depends

from ...core.security import get_current_active_user
from ...models import User
from ...schemas import UserOut

router = APIRouter()


# ...existing endpoints, update all imports to new structure...
# ...update all endpoints to use current_user: User = Depends(get_current_active_user)...
