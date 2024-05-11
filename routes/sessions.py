from typing import List
from fastapi import APIRouter, HTTPException, status
from models.sessionModel import Session, SessionCreate
from database import Sessions
import logging

router = APIRouter()

async def check_if_session_exists(session_id: str) -> bool:
    session = await Sessions.find_one({"sessionID": session_id})
    return session is not None

@router.post("/", response_model=Session)
async def create_session(session_input: SessionCreate):
    session_id = session_input.sessionID
    if await check_if_session_exists(session_id):
        logging.error(f"Attempt to create a session that already exists: {session_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already exists")

    try:
        session = Sessions(**session_input.dict())
        await session.insert()
        return session
    except Exception as e:
        logging.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[Session])
async def get_all_sessions():
    try:
        sessions = await Sessions.find_all().to_list()
        return sessions
    except Exception as e:
        logging.error(f"Failed to retrieve sessions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    session = await Sessions.find_one({"sessionID": session_id})
    if session:
        return session
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

@router.put("/{session_id}", response_model=Session)
async def update_session(session_id: str, session_update: SessionCreate):
    if not await check_if_session_exists(session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        updated_session = await Sessions.find_one_and_replace(
            {"sessionID": session_id}, session_update.dict(), return_document=True
        )
        return updated_session
    except Exception as e:
        logging.error(f"Failed to update session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{session_id}")  # Assuming a base path of /sessions for all session-related operations
async def delete_session(session_id: str):
    """
    Deletes a session by its ID from the database. Raises a 404 error if the session is not found,
    and a 500 error if there is an error during the deletion process.
    """
    if not await check_if_session_exists(session_id):
        logging.warning(f"Attempt to delete a non-existent session: {session_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        await Sessions.find_one_and_delete({"sessionID": session_id})
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logging.error(f"Failed to delete session_test: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
