from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from pydantic import BaseModel
from typing import Annotated, Optional
from controllers.usuarioController import UsuarioController
from controllers.pacienteController import PacienteController
from controllers.citaController import CitaController
from utils.auth import decode_access_token

router = APIRouter()
usuario_controller = UsuarioController()
paciente_controller = CitaController()

class DatosEspecificosRequest(BaseModel):
    peso: float
    altura: float
    enfermedades: str

@router.get("/citas", response_model=dict)
async def get_citas_paciente(current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="Solo pacientes pueden ver sus citas")
    return paciente_controller.get_citas_paciente(current_user["usuario_id"])

@router.get("/citas/proxima", response_model=dict)
async def get_proxima_cita(current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="Solo pacientes pueden ver su próxima cita")
    return paciente_controller.get_proxima_cita(current_user["usuario_id"])

@router.get("/citas/ultima", response_model=dict)
async def get_ultima_cita(current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="Solo pacientes pueden ver su última cita")
    return paciente_controller.get_ultima_cita(current_user["usuario_id"])

@router.post("/citas", response_model=dict)
async def crear_cita_paciente(
    medico_id: Annotated[int, Form()],
    fecha: Annotated[str, Form()],
    hora: Annotated[str, Form()],
    especialidad_id: Annotated[Optional[int], Form()] = None, 
    
    # Archivos (Multipart File)
    imagenes: Annotated[list[UploadFile], File()] = [], current_user: dict = Depends(decode_access_token)):
    print("📥 Datos recibidos:")
    print(f"  medico_id: {medico_id}")
    print(f"  fecha: {fecha}")
    print(f"  hora: {hora}")
    print(f"  especialidad: {especialidad_id}")
    print(f"  imagenes: {len(imagenes) if imagenes else 0}")

    # Procesar imágenes si las hay
    if imagenes:
        for imagen in imagenes:
            print(f"  📷 Imagen: {imagen.filename} ({imagen.size} bytes)")
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="Solo pacientes pueden agendar citas")
    return await paciente_controller.crear_cita(current_user["usuario_id"], medico_id, fecha, hora, especialidad_id, imagenes)

@router.get("/historial")
async def get_historial_paciente(current_user: dict = Depends(decode_access_token), fecha: Optional[str] = None, rango: Optional[str] = None):
        usuario_id = current_user.get("usuario_id")
        if usuario_id is None or current_user["rol_id"] != 1:
            raise HTTPException(status_code=403, detail="No tiene permisos para ver el historial de paciente")
        return paciente_controller.get_historial_paciente(usuario_id=usuario_id, fecha=fecha, rango=rango)

@router.get("/especialidades", response_model=dict)
async def get_especialidades(current_user: dict = Depends(decode_access_token)):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver las especialidades")
    return paciente_controller.get_especialidades()
    

@router.get("/medicos", response_model=dict)
async def get_medicos(current_user: dict = Depends(decode_access_token), especialidad_id: int = None):
    if current_user["rol_id"] != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver los médicos")
    return paciente_controller.get_medicos(especialidad_id)