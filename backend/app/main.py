import os
from fastapi import FastAPI, UploadFile, File, HTTPException

from app.services.ocr_service import extract_text_from_image
from app.services.pdf_service import extract_text_from_pdf
from app.services.extraction_service import extract_basic_fields

app  = FastAPI(title="Swasthya Doc AI")

@app.get("/")
def root():
    return{"message": "Swasthya Doc AI is running"}

@app.post("/upload")
#In Python, ... is a built-in singleton object called Ellipsis
#FastAPI and Pydantic use ... to mean: "This field is required, and there is no default value."
async def upload_file(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Branch by file type to extract text
    if file.filename.lower().endswith(".pdf"):
        ocr_text = extract_text_from_pdf(file_path)
    elif file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        ocr_text = extract_text_from_image(file_path)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload PDF, PNG, or JPG."
        )
    # Run extraction (Regex + ONNX LLM)
    prescription_data = extract_basic_fields(ocr_text)
    return {
        "filename": file.filename,
        "data": prescription_data
    }