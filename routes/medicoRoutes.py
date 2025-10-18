from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from controllers.citaController import CitaController
from utils.auth import decode_access_token

router = APIRouter()
controller = CitaController()

class AtencionRequest(BaseModel):
    sintomas: str
    diagnostico: str
    recomendaciones: str

class PacienteHistorialRequest(BaseModel):
    nombre: str | None = None
    identificacion: str | None = None
    fecha: str | None = None
    rango: str | None = None

@router.get("/historial", response_model=dict)
async def get_historial_medico(request: PacienteHistorialRequest, current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 2:
        raise HTTPException(status_code=403, detail="Solo médicos pueden ver historial de pacientes")
    return controller.get_historial_medico(request.nombre, request.identificacion, current_user["usuario_id"], request.fecha, request.rango)

@router.post("/atencion", response_model=dict)
async def registrar_atencion(request: AtencionRequest, paciente_id: int, current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 2:
        raise HTTPException(status_code=403, detail="Solo médicos pueden registrar atención")
    return controller.registrar_atencion(paciente_id, current_user["usuario_id"], request.sintomas, request.diagnostico, request.recomendaciones)