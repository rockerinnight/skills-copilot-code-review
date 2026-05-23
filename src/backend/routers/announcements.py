"""
Announcement endpoints for the High School Management System API
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


def _validate_teacher(teacher_username: Optional[str]) -> Dict[str, Any]:
    """Validate teacher/admin identity for protected routes."""
    if not teacher_username:
        raise HTTPException(status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    return teacher


def _parse_date(value: Optional[str], field_name: str, required: bool = False) -> Optional[str]:
    """Validate and normalize dates to YYYY-MM-DD."""
    if not value:
        if required:
            raise HTTPException(status_code=400, detail=f"{field_name} is required")
        return None

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
        return parsed.isoformat()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"{field_name} must use YYYY-MM-DD format")


def _serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(announcement["_id"]),
        "message": announcement.get("message", ""),
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement.get("expiration_date"),
        "created_by": announcement.get("created_by"),
        "updated_by": announcement.get("updated_by"),
        "created_at": announcement.get("created_at"),
        "updated_at": announcement.get("updated_at")
    }


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get currently active announcements for all users."""
    today = date.today().isoformat()
    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$exists": False}},
            {"start_date": {"$lte": today}}
        ]
    }

    announcements = announcements_collection.find(query).sort("expiration_date", 1)
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.get("/all", response_model=List[Dict[str, Any]])
def get_all_announcements(teacher_username: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """Get all announcements, including expired ones, for announcement management."""
    _validate_teacher(teacher_username)

    announcements = announcements_collection.find({}).sort("created_at", -1)
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any])
def create_announcement(
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Create a new announcement."""
    teacher = _validate_teacher(teacher_username)

    message_text = message.strip()
    if not message_text:
        raise HTTPException(status_code=400, detail="message is required")

    normalized_start_date = _parse_date(start_date, "start_date")
    normalized_expiration_date = _parse_date(expiration_date, "expiration_date", required=True)

    if normalized_start_date and normalized_start_date > normalized_expiration_date:
        raise HTTPException(status_code=400, detail="start_date cannot be later than expiration_date")

    now = datetime.utcnow().isoformat()
    announcement = {
        "message": message_text,
        "start_date": normalized_start_date,
        "expiration_date": normalized_expiration_date,
        "created_by": teacher["username"],
        "updated_by": teacher["username"],
        "created_at": now,
        "updated_at": now
    }

    result = announcements_collection.insert_one(announcement)
    created = announcements_collection.find_one({"_id": result.inserted_id})
    return _serialize_announcement(created)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Update an existing announcement."""
    teacher = _validate_teacher(teacher_username)

    message_text = message.strip()
    if not message_text:
        raise HTTPException(status_code=400, detail="message is required")

    normalized_start_date = _parse_date(start_date, "start_date")
    normalized_expiration_date = _parse_date(expiration_date, "expiration_date", required=True)

    if normalized_start_date and normalized_start_date > normalized_expiration_date:
        raise HTTPException(status_code=400, detail="start_date cannot be later than expiration_date")

    try:
        object_id = ObjectId(announcement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid announcement ID")

    update_payload = {
        "message": message_text,
        "start_date": normalized_start_date,
        "expiration_date": normalized_expiration_date,
        "updated_by": teacher["username"],
        "updated_at": datetime.utcnow().isoformat()
    }

    result = announcements_collection.update_one(
        {"_id": object_id},
        {"$set": update_payload}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    updated = announcements_collection.find_one({"_id": object_id})
    return _serialize_announcement(updated)


@router.delete("/{announcement_id}", response_model=Dict[str, str])
def delete_announcement(
    announcement_id: str,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, str]:
    """Delete an announcement."""
    _validate_teacher(teacher_username)

    try:
        object_id = ObjectId(announcement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid announcement ID")

    result = announcements_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
