from pydantic import BaseModel

#Structure that our llm output must follow.
class Medicine(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None


class Prescription(BaseModel):
    patient_name: str | None = None
    doctor_name: str | None = None
    date: str | None = None
    diagnosis: str | None = None
    medicines: list[Medicine] = []
