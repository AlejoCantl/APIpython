from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from controllers.medicoController import MedicoController
from utils.auth import decode_access_token

router = APIRouter()
controller = MedicoController()

class AtencionRequest(BaseModel):
    sistema: str
    diagnostico: str
    recomendaciones: str

# controllers/medicoController.py
@router.get("/historial", response_model=dict)
async def get_historial_medico(current_user: dict = Depends(decode_access_token), nombre: str | None = None, identificacion: str | None = None, usuario_id: int | None = None, fecha: str | None = None, rango: str | None = None):
    # ← ¡ORDEN CORRECTO!
    if current_user["rol_id"] != 2:
        raise HTTPException(status_code=403, detail="Solo médicos pueden ver el historial médico")
    return controller.get_historial_medico(
        usuario_id=current_user["usuario_id"],
        nombre=nombre,
        identificacion=identificacion,
        fecha=fecha,
        rango=rango
    )


# routes/medicoRoutes.py

@router.post("/atencion", response_model=dict)
async def registrar_atencion(
    # CAMBIO: Usar Annotated con Form() para forzar a FastAPI a leer del Form Data
    cita_id: int = Form(...),
    sistema: str = Form(...),
    diagnostico: str = Form(...),
    recomendaciones: str = Form(...),
    imagenes: list[UploadFile] = File([]),
    current_user: dict = Depends(decode_access_token)
):
    if current_user["rol_id"] != 2:
        raise HTTPException(status_code=403, detail="Solo médicos pueden registrar atención")
        
    return controller.registrar_atencion(
        cita_id, 
        sistema,           # <--- Cambiado de request.sistema a sistema
        diagnostico, 
        recomendaciones, 
        imagenes
    )


@router.get("/citas/aprobadas", response_model=dict)
async def get_citas_aprobadas(current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 2:
        raise HTTPException(status_code=403, detail="Solo médicos pueden ver citas aprobadas")
    return controller.get_paciente_citas_aprobadas(current_user["usuario_id"])

@router.get("/paciente/{paciente_id}", response_model=dict)
async def get_paciente_info(paciente_id: int, current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 2:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return controller.get_paciente_info(paciente_id)