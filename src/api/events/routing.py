from fastapi import APIRouter
from schema import EventSchema

router = APIRouter()

@router.get("/")
def read_events():
    return {
        "items":"test"
    } 

@router.get("/{event_id}")
def get_event(event_id:int) -> EventSchema:
    return {"id": event_id}