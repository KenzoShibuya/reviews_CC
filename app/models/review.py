from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    target_user_id: int
    transaction_id: str
    rating: float = Field(..., ge=1, le=5)
    comment: str
