"""Announcement endpoints for the High School Management System API."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator

from ..database import announcements_collection, teachers_collection

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementPayload(BaseModel):
    """Fields shared by announcement creation and updates."""

    message: str = Field(..., min_length=1, max_length=500)
    start_date: Optional[date] = None
    expiration_date: date

    @validator("expiration_date")
    def expiration_must_follow_start(cls, expiration_date, values):
        start_date = values.get("start_date")
        if start_date and expiration_date < start_date:
            raise ValueError("Expiration date must be on or after the start date")
        return expiration_date


def _require_teacher(username: str) -> None:
    """Require a valid signed-in teacher for management operations."""
    if not username or not teachers_collection.find_one({"_id": username}):
        raise HTTPException(status_code=401, detail="Authentication required")


def _serialize(announcement: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": announcement["_id"],
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement["expiration_date"],
    }


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get announcements that are active today for the public banner."""
    today = date.today().isoformat()
    announcements = announcements_collection.find({
        "$and": [
            {"$or": [{"start_date": None}, {"start_date": {"$lte": today}}]},
            {"expiration_date": {"$gte": today}},
        ]
    }).sort("expiration_date", 1)
    return [_serialize(announcement) for announcement in announcements]


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(
    teacher_username: str = Query(...)
) -> List[Dict[str, Any]]:
    """Get all announcements for an authenticated teacher."""
    _require_teacher(teacher_username)
    announcements = announcements_collection.find().sort("expiration_date", 1)
    return [_serialize(announcement) for announcement in announcements]


@router.post("", response_model=Dict[str, Any])
def create_announcement(
    announcement: AnnouncementPayload,
    teacher_username: str = Query(...)
) -> Dict[str, Any]:
    """Create an announcement for an authenticated teacher."""
    _require_teacher(teacher_username)
    announcement_id = str(uuid4())
    document = {
        "_id": announcement_id,
        "message": announcement.message.strip(),
        "start_date": announcement.start_date.isoformat() if announcement.start_date else None,
        "expiration_date": announcement.expiration_date.isoformat(),
    }
    if not document["message"]:
        raise HTTPException(status_code=400, detail="Message is required")
    announcements_collection.insert_one(document)
    return _serialize(document)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    announcement: AnnouncementPayload,
    teacher_username: str = Query(...)
) -> Dict[str, Any]:
    """Update an announcement for an authenticated teacher."""
    _require_teacher(teacher_username)
    document = {
        "message": announcement.message.strip(),
        "start_date": announcement.start_date.isoformat() if announcement.start_date else None,
        "expiration_date": announcement.expiration_date.isoformat(),
    }
    if not document["message"]:
        raise HTTPException(status_code=400, detail="Message is required")
    result = announcements_collection.update_one({"_id": announcement_id}, {"$set": document})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return _serialize({"_id": announcement_id, **document})


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    teacher_username: str = Query(...)
) -> Dict[str, str]:
    """Delete an announcement for an authenticated teacher."""
    _require_teacher(teacher_username)
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted"}