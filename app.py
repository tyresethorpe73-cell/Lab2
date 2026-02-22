from pydantic import BaseModel, Field
from fastapi import FastAPI,status,HTTPException
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

app = FastAPI()

# Bonus Question
# Just declaring the possibilities for the "Priority" and the "status". 
class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Status(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class MaintenanceRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    equipment_name: str
    description: str
    priority: Priority
    status: Status
    technician: str
    department: str

records: dict[UUID, MaintenanceRecord] = {}

class MaintenanceRecordUpdate(BaseModel):
    equipment_name: str | None = None
    description: str | None = None
    priority: Priority | None = None
    status: Status | None = None
    technician: str | None = None
    department: str | None = None


@app.get("/")
def root():
    return {"message": "Maintenace API is running"}

# Needs everything from equipment name down to department.
@app.post("/records", status_code=status.HTTP_201_CREATED)
def create_record(record: MaintenanceRecord):
    records[record.id] = record
    return record

@app.get("/records")
def fetch_all_records():
    return list(records.values())

@app.get("/records/{record_id}")
def get_all_by_id(record_id: UUID):
    if record_id not in records:
        raise HTTPException(status_code=404, detail= "Resource not found !!")
    return records[record_id]

@app.put("/records/{record_id}")
def updating_records(record_id: UUID, record: MaintenanceRecord):
# checking if there is any record attaced to such UUID
    if record_id in records:
        original_created_at = records[record_id].created_at

        record.id = record_id
        record.created_at = original_created_at
        record.updated_at = datetime.now()
        
        records[record_id] = record
        return record
    
    # If record does NOT exist the the put simply creates it
    record.id = record_id
    record.created_at = datetime.now()
    record.updated_at = datetime.now()
    
    records[record_id] = record
    return record

# Partial replacement/PATCH 
@app.patch("/records/{record_id}")
def patch_record(record_id: UUID, record_update: MaintenanceRecordUpdate):
    if record_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    
    existing_record = records[record_id]
    
    update_data = record_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(existing_record, field, value)
    
    existing_record.updated_at = datetime.now()
    
    return existing_record

@app.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: UUID):
    if record_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    
    del records[record_id]



