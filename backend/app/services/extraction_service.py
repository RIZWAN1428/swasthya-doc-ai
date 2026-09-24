import re

from app.schemas.prescription import Prescription
from app.services.llm_service import parse_medicines

def extract_basic_fields(ocr_text: list[str]) -> Prescription:
    text = "\n".join(ocr_text)

    patient_name = None
    doctor_name = None
    date = None
    raw_medicine_lines: list[str] = []

    name_match = re.search(
        r"Name\s*\n([A-Za-z ]+)",
        text,
        re.IGNORECASE,
    )
    doctor_match = re.search(
        r"Doctor\s*\n([A-Za-z ]+)",
        text,
        re.IGNORECASE,
    )

    date_match = re.search(
        r"Episode Date\s*:?\s*\n?(\d{2}/\d{2}/\d{4})",
        text,
        re.IGNORECASE,
    )

    

    if name_match:
        patient_name = name_match.group(1).strip()

    if doctor_match:
        doctor_name = doctor_match.group(1).strip()

    if date_match:
        date = date_match.group(1).strip()

    for line in ocr_text:
        line = line.strip()
        
        if re.match(r"^Review after\b", line, re.IGNORECASE):
            break

        if re.match(r"^(Tablet|Tab|Capsule|Cap)\b", line, re.IGNORECASE):
            raw_medicine_lines.append(line)
        elif raw_medicine_lines:
            raw_medicine_lines[-1] += " " + line
    
    structured_medicines = (
        parse_medicines(raw_medicine_lines) if raw_medicine_lines else []
    ) 
    return Prescription(
        patient_name=patient_name,
        doctor_name=doctor_name,
        date=date,
        medicines=structured_medicines,
    )

    