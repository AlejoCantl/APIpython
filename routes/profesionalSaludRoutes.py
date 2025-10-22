from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from controllers.profesionalSaludControler import ProfesionalSaludController
from utils.auth import decode_access_token

router = APIRouter()
controller = ProfesionalSaludController()

class AprobarCitaRequest(BaseModel):
    cita_id: int
    aprobado: bool
    razon: str | None = None

@router.get("/citas", response_model=dict)
async def get_citas_profesional(current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 3:
        raise HTTPException(status_code=403, detail="Solo profesionales de la salud pueden ver citas")
    return controller.get_citas_profesional()

@router.patch("/citas/aprobar", response_model=dict)
async def aprobar_cita(request: AprobarCitaRequest, current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 3:
        raise HTTPException(status_code=403, detail="Solo profesionales de la salud pueden aprobar citas")
    return controller.aprobar_cita(request.cita_id, request.aprobado, request.razon, current_user["usuario_id"])

@router.get("/citas/{cita_id}/detalle", response_model=dict)
async def get_detalle_cita(cita_id: int, current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 3:
        raise HTTPException(status_code=403, detail="Solo profesionales de la salud pueden ver detalles de citas")
    return controller.get_detalle_cita(cita_id)