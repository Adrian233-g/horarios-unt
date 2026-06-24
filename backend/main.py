from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import (
    auth, usuarios,
    facultades, departamentos, escuelas, aulas, laboratorios, docentes,
    semestres, cursos, asignaciones, carga_no_lectiva, curriculas,
)
from routers import horarios, documentos
from ws_manager import manager as ws_manager

from seed_data import run as run_seed_data

app = FastAPI(title="UNT Horarios API")

@app.get("/api/seed_database_secret")
def seed_db():
    try:
        run_seed_data()
        return {"msg": "Base de datos poblada exitosamente"}
    except Exception as e:
        return {"error": str(e)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(facultades.router)
app.include_router(departamentos.router)
app.include_router(escuelas.router)
app.include_router(aulas.router)
app.include_router(laboratorios.router)
app.include_router(docentes.router)
app.include_router(semestres.router)
app.include_router(cursos.router)
app.include_router(asignaciones.router)
app.include_router(carga_no_lectiva.router)
app.include_router(horarios.router)
app.include_router(curriculas.router)
app.include_router(documentos.router)


@app.websocket("/ws/horarios")
async def websocket_horarios(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
