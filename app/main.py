from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import uuid
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from sqlmodel import Session, select
from app.core.agents import Orchestrator
from app.core.db import create_db_and_tables, get_session, User, Report
from app.core.auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Research Agent API", version="2.0.0", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to Research Agent API - v4.0 (Full GitOps Loop Verified!)"}

# --- Pydantic Models for API ---
class ResearchRequest(BaseModel):
    topic: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ReportResponse(BaseModel):
    report_id: str
    topic: str
    status: str
    content: Optional[str]

# --- Background Task ---
async def run_research_task(report_id: str, topic: str, user_id: int, session_factory):
    # Note: Issues with threading and SQLModel sessions in background tasks.
    # We create a fresh session here.
    with session_factory() as session:
        # 1. Update status to processing
        statement = select(Report).where(Report.report_id == report_id)
        report = session.exec(statement).first()
        if report:
            report.status = "processing"
            session.add(report)
            session.commit()
    
    orchestrator = Orchestrator()
    try:
        result = await orchestrator.generate_report(topic)
        
        # Save completion
        with session_factory() as session:
            statement = select(Report).where(Report.report_id == report_id)
            report = session.exec(statement).first()
            if report:
                report.status = "completed"
                report.content = json.dumps(result) # Store as JSON string
                session.add(report)
                session.commit()
                
    except Exception as e:
        # Save failure
        with session_factory() as session:
            statement = select(Report).where(Report.report_id == report_id)
            report = session.exec(statement).first()
            if report:
                report.status = "failed"
                report.content = json.dumps({"error": str(e)})
                session.add(report)
                session.commit()

# --- Auth Endpoints ---

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pwd)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Research Endpoints ---

@app.post("/research", summary="Start a new research task")
async def start_research(
    request: ResearchRequest, 
    background_tasks: BackgroundTasks, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    report_id = str(uuid.uuid4())
    
    # Create initial report entry
    new_report = Report(
        report_id=report_id, 
        topic=request.topic, 
        status="queued", 
        user_id=current_user.id
    )
    session.add(new_report)
    session.commit()
    
    # Pass session factory wrapper or handle session carefully in background
    # For simplicity in this demo, we re-instantiate engine in background helper logic 
    # but strictly passing `Session` across threads is unsafe.
    # We will pass a fresh session generator concept or just use the global engine.
    from sqlmodel import Session
    from app.core.db import engine
    def session_factory():
        return Session(engine)

    background_tasks.add_task(run_research_task, report_id, request.topic, current_user.id, session_factory)
    
    return {"message": "Research started", "report_id": report_id}

@app.get("/research/{report_id}")
async def get_report(report_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Report).where(Report.report_id == report_id)
    report = session.exec(statement).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Optional: Check if report belongs to user
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this report")

    data = None
    if report.content:
        data = json.loads(report.content)
        
    return {
        "report_id": report.report_id,
        "status": report.status,
        "topic": report.topic,
        "data": data
    }

@app.get("/history", response_model=List[ReportResponse])
async def get_history(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Report).where(Report.user_id == current_user.id).order_by(Report.created_at.desc())
    reports = session.exec(statement).all()
    
    response_data = []
    for r in reports:
        response_data.append({
            "report_id": r.report_id,
            "topic": r.topic,
            "status": r.status,
            "content": r.content
        })
    return response_data

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
