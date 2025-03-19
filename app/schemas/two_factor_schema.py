from pydantic import BaseModel

class TwoFactorVerifyRequest(BaseModel):
    user_id: int
    token: str
