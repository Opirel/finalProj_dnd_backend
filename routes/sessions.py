from typing import List
from fastapi import APIRouter, HTTPException, status
from models.sessionModel import SessionMD, SessionCreate
from database import Sessions
import logging
from icecream import ic  # Import ic for debugging

router = APIRouter()

async def check_if_session_exists(session_id: str) -> bool:
    session = await Sessions.find_one({"sessionID": session_id})
    ic(session)  # Debug output
    return session is not None

@router.post("/", response_model=SessionMD)
async def create_session(session_input: SessionMD):
    session_id = session_input.sessionID
    if await check_if_session_exists(session_id):
        logging.error(f"Attempt to create a session that already exists: {session_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already exists")

    try:
        session = Sessions(**session_input.dict())
        await session.insert()
        return await Sessions.get(session.id)
    except Exception as e:
        logging.error(f"Failed to create session: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[SessionMD])
async def get_all_sessions():
    try:
        sessions = await Sessions.find({}).to_list(None)
        ic(sessions)  # Debug session list
        return sessions
    except Exception as e:
        logging.error(f"Failed to retrieve sessions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{session_id}", response_model=SessionMD)
async def get_session(session_id: str):
    session = await Sessions.find_one({"sessionID": session_id})
    ic(session)  # Debug the retrieved session
    if session:
        return session
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

@router.put("/{session_id}", response_model=SessionMD)
async def update_session(session_id: str, session_update: SessionCreate):
    session = await Sessions.find_one(Sessions.sessionID == session_id)
    ic(session)  # Debug the session before update
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        session.messages = session_update.messages
        await session.save()
        ic(session)  # Debug the updated session
        return session
    except Exception as e:
        logging.error(f"Failed to update session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{session_id}", response_model=dict)
async def delete_session(session_id: str):
    if not await check_if_session_exists(session_id):
        logging.warning(f"Attempt to delete a non-existent session: {session_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        sessions_data = await Sessions.find_one(Sessions.sessionID == session_id)
        ic(sessions_data)  # Debug the session to be deleted
        await sessions_data.delete()
        return {"message": "session deleted successfully"}
    except Exception as e:
        logging.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
