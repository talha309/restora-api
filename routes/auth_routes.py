# restora-api/routes/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db                                      # ✅ fixed: was database.database
from models.user_model import User, Role
from schemas.user_schema import UserCreate, UserLogin, UserOut, TokenOut
from utils.auth_util import hash_password, verify_password, create_access_token  # ✅ fixed: was auth_utils
from datetime import datetime

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # Validate role value
    valid_roles = [r.value for r in Role]
    if user.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )

    # check email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # check username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # hash password and save — include created_at (was missing, non-nullable field)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=Role(user.role),          # ✅ fixed: convert str → Role enum
        created_at=datetime.utcnow()   # ✅ fixed: was missing entirely
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenOut)
def login(user: UserLogin, db: Session = Depends(get_db)):

    # check user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # verify password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # create token — role stored as string value so get_current_user can read it
    token = create_access_token(data={
        "sub": str(db_user.id),
        "role": db_user.role.value    # ✅ fixed: .value converts enum → string
    })

    return {"access_token": token, "token_type": "bearer"}