from fastapi import FastAPI, UploadFile, File

app  = FastAPI(title="Swasthya Doc AI")

@app.get("/")
def root():
    return{"message": "Swasthya Doc AI is running"}

@app.post("/upload")
#In Python, ... is a built-in singleton object called Ellipsis
#FastAPI and Pydantic use ... to mean: "This field is required, and there is no default value."
async def upload_file(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return{
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File uploaded successfully"
    }