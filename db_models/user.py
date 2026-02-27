from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, DeclarativeMeta
from typing import Dict, Any
from models.base_models import RegisterUserResponse

Base: DeclarativeMeta = declarative_base()


class UserDBModel(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    email = Column(String)
    full_name = Column(String)
    password = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    verified = Column(Boolean)
    banned = Column(Boolean)
    roles = Column(String)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в Pydantic модель RegisterUserResponse."""
        data = {
            "id": self.id,
            "email": self.email,
            "fullName": self.full_name,
            "password": self.password,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at,
            "verified": self.verified,
            "banned": self.banned,
            "roles": [self.roles] if isinstance(self.roles, str) else self.roles,
        }
        return RegisterUserResponse(**data)

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"

    @classmethod
    def from_payload(cls, payload) -> "UserDBModel":
        """Создать экземпляр UserDBModel из UserDBCreatePayload (не коммитит)."""
        data = payload.model_dump(by_alias=True, exclude_none=True)
        return cls(**data)
