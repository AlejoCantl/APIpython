from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from controllers.usuarioController import UsuarioController
from controllers.citaController import CitaController
from utils.auth import decode_access_token

router = APIRouter()
usuario_controller = UsuarioController()
cita_controller = CitaController()

class CitaRequest(BaseModel):
    medico_id: int
    fecha: str
    motivo: str

class DatosEspecificosRequest(BaseModel):
    peso: float
    altura: float
    enfermedades: str

@router.get("/citas", response_model=dict)
async def get_citas_paciente(current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="Solo pacientes pueden ver sus citas")
    return cita_controller.get_citas_paciente(current_user["usuario_id"])

@router.post("/citas", response_model=dict)
async def crear_cita_paciente(request: CitaRequest, current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="Solo pacientes pueden agendar citas")
    return cita_controller.crear_cita(current_user["usuario_id"], request.medico_id, request.fecha, request.motivo)

@router.get("/historial", response_model=dict)
async def get_historial_paciente(fecha: str | None = None, rango: str | None = None, current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="Solo pacientes pueden ver su historial")
    return cita_controller.get_historial_paciente(current_user["usuario_id"], fecha, rango)

@router.put("/datos-especificos", response_model=dict)
async def actualizar_datos_especificos(request: DatosEspecificosRequest, current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="Solo pacientes pueden actualizar datos específicos")
    return usuario_controller.actualizar_datos_especificos(current_user["usuario_id"], request.dict())