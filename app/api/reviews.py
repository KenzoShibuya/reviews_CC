from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from app.models.review import ReviewCreate
from app.db.mongodb import db
from app.middleware.auth import get_current_user_id

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

@router.post("")
async def create_review(review: ReviewCreate, user_id: int = Depends(get_current_user_id)):
    try:
        review_doc = review.model_dump()
        review_doc["user_id"] = user_id
        review_doc["created_at"] = datetime.now(timezone.utc)

        result = await db.reviews_collection.insert_one(review_doc)
        return {"message": "Review creada", "id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error al crear review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_reviews(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    cursor = db.reviews_collection.find({"target_user_id": user_id})
    reviews = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        reviews.append(document)
    return reviews

@router.get("/stats/{user_id}")
async def get_user_review_stats(user_id: int, current_user_id: int = Depends(get_current_user_id)):
    pipeline = [
        {"$match": {"target_user_id": user_id}},
        {"$group": {
            "_id": "$target_user_id",
            "average_rating": {"$avg": "$rating"},
            "total_reviews": {"$sum": 1}
        }}
    ]
    cursor = db.reviews_collection.aggregate(pipeline)
    stats = await cursor.to_list(length=1)

    if stats:
        return stats[0]
    return {"_id": user_id, "average_rating": 0, "total_reviews": 0}
