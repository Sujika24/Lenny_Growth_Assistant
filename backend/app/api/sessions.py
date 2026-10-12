from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.session_service import SessionService
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse, SessionDetailResponse
from app.schemas.message import MessageResponse

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    return SessionService.create_session(db, session_in)


@router.get("", response_model=List[SessionResponse])
def list_sessions(user_id: str = "anonymous", db: Session = Depends(get_db)):
    return SessionService.list_sessions(db, user_id=user_id)


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    db_session = SessionService.get_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(session_id: str, update_in: SessionUpdate, db: Session = Depends(get_db)):
    db_session = SessionService.update_session(db, session_id, update_in)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    success = SessionService.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return None


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    db_session = SessionService.get_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionService.get_messages(db, session_id)
