from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Gets a user by username.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Gets a user by email.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, hashed_password: str, email: str = None) -> User:
    """
    Creates a new user in the database.
    """
    db_user = User(username=username, hashed_password=hashed_password, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_username(db: Session, user: User, new_username: str) -> User:
    """
    Updates an existing user's username.
    """
    user.username = new_username
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_password(db: Session, user: User, new_hashed_password: str) -> User:
    """
    Updates an existing user's password.
    """
    user.hashed_password = new_hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User) -> None:
    """
    Deletes a user from the database.
    """
    db.delete(user)
    db.commit()