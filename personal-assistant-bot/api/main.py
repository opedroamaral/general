import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import settings
from api.auth import create_token
from api.routes.tasks import router as tasks_router
from api.routes.routines import router as routines_router
from api.routes.notes import router as notes_router
from api.routes.businesses import router as businesses_router
from db.session import get_db
from db.queries.tasks import get_tasks, get_overdue_tasks, get_tasks_due_today
from db.queries.routines import get_routines, get_routines_for_today
from db.queries.notes import get_notes
from db.queries.businesses import get_businesses
from api.auth import verify_token
from fastapi import Depends

app = FastAPI(title="Gestor Pessoal API", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router, prefix="/api")
app.include_router(routines_router, prefix="/api")
app.include_router(notes_router, prefix="/api")
app.include_router(businesses_router, prefix="/api")


class LoginBody(BaseModel):
    password: str


@app.post("/api/auth/login")
def login(body: LoginBody):
    if body.password != settings.dashboard_password:
        raise HTTPException(401, "Senha incorreta")
    return {"access_token": create_token(), "token_type": "bearer"}


@app.get("/api/stats", dependencies=[Depends(verify_token)])
def stats():
    db = next(get_db())
    try:
        pending = get_tasks(db, status="pending")
        overdue = get_overdue_tasks(db)
        today_tasks = get_tasks_due_today(db)
        today_routines = get_routines_for_today(db)
        active_businesses = get_businesses(db, active=True)
        recent_notes = get_notes(db, limit=5)

        return {
            "tasks": {
                "pending": len(pending),
                "overdue": len(overdue),
                "due_today": len(today_tasks),
            },
            "routines": {
                "today": len(today_routines),
                "done_today": sum(
                    1 for r in today_routines
                    if r.last_done and r.last_done.isoformat() == __import__("datetime").date.today().isoformat()
                ),
            },
            "businesses": len(active_businesses),
            "notes_total": len(get_notes(db, limit=9999)),
        }
    finally:
        db.close()


# Serve React build
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        index = os.path.join(frontend_dist, "index.html")
        return FileResponse(index)
