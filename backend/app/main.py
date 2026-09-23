from fastapi import FastAPI

app  = FastAPI(title="Swasthya Doc AI")

@app.get("/")
def root():
    return{"message": "Swasthya Doc AI is running"}