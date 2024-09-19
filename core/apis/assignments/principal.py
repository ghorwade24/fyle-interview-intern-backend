import datetime
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core import db
import json
from models import Assignment, Teacher
from tests.conftest import h_principal

app = FastAPI()

def get_db():
    try:
        yield db
    finally:
        db.close()
        
def get_principal(x_principal: str):
    # Mock parsing, assumes header is correctly formatted JSON
    
    try:
        principal = json.loads(x_principal)
        return principal
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid principal header")
        
@app.get("/principal/assignments")
def list_assignments(db: Session = Depends(get_db), principal: dict = Depends(h_principal)):
    assignments = db.query(Assignment).all()
    return {"data": [assignment.__dict__ for assignment in assignments]}

@app.get("/principal/teachers")
def list_teachers(db: Session = Depends(get_db), principal: dict = Depends(h_principal)):
    teachers = db.query(Teacher).all()
    return {"data": [teacher.__dict__ for teacher in teachers]}

# POST /principal/assignments/grade
@app.post("/principal/assignments/grade")
def grade_assignment(payload: dict, db: Session = Depends(get_db), principal: dict = Depends(h_principal)):
    assignment_id = payload.get("id")
    grade = payload.get("grade")

    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Update assignment grade and state
    assignment.grade = grade
    assignment.state = "GRADED"
    assignment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assignment)

    return {"data": assignment.__dict__}