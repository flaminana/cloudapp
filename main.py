from fastapi import FastAPI
from routers import objective, pronunciation, daily_conversation, translation

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI() # ✅ First, create the app

# ✅ Then mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Include routers
app.include_router(objective.router)
app.include_router(pronunciation.router)
app.include_router(daily_conversation.router)
app.include_router(translation.router)


# ✅ Serve test HTML page
@app.get("/test-objective")
def serve_test_page():
    return FileResponse(os.path.join("static", "objective_test.html"))
from fastapi import FastAPI
from routers import objective, pronunciation, daily_conversation

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI() # ✅ First, create the app

# ✅ Then mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Include routers
app.include_router(objective.router)
app.include_router(pronunciation.router)
app.include_router(daily_conversation.router)

# ✅ Serve test HTML page
@app.get("/test-objective")
def serve_test_page():
    return FileResponse(os.path.join("static", "objective_test.html"))
