from fastapi import FastAPI
from routes.usuarioRoutes import router as usuario_router
from routes.pacienteRoutes import router as paciente_router
from routes.medicoRoutes import router as medico_router
from routes.profesionalSaludRoutes import router as profesional_salud_router

app = FastAPI()
app.include_router(usuario_router, prefix="/Usuario")
app.include_router(paciente_router, prefix="/Paciente")
app.include_router(medico_router, prefix="/Medico")
app.include_router(profesional_salud_router, prefix="/Profesional_salud")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)