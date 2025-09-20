from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import db, models, auth as auth_utils
from ..schemas import Token, UserCreate

router = APIRouter()

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)):
    user = auth_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_utils.create_token_response(user)

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(db.get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth_utils.get_password_hash(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return auth_utils.create_token_response(user)
