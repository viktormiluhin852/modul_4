from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationError

from constants.roles import Roles


class UserData(BaseModel):
    email: str
    fullName: str
    password: str = Field(..., min_length=8)
    passwordRepeat: str
    roles: list[Roles]
    banned: Optional[bool]
    verified: Optional[bool]

    @field_validator("email")
    def check_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Некорректный email! В поле email отсутствует символ '@'")

        return value


try:
    print(UserData(**{
            "email": "random@email",
            "fullName": "random_name",
            "password": "random_password",
            "passwordRepeat": "random_password",
            "roles": [Roles.SUPER_ADMIN.value]
    }))
except ValidationError as e:
    print(e)



