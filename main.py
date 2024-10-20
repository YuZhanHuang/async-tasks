from project import create_app

app = create_app()
celery = app.celery_app


@app.get("/")
async def root():
    return {"message": "Hello World"}

