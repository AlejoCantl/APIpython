from fastapi import APIRouter, Depends
from pydantic import BaseModel
from controllers.usuarioController import UsuarioController
from utils.auth import decode_access_token

router = APIRouter()
controller = UsuarioController()

class LoginRequest(BaseModel):
    nombre_usuario: str
    contrasena: str

class UserProfile(BaseModel):
    nombre: str
    apellido: str
    correo: str
    edad: int
    ubicacion: str
    identificacion: str
    rol: str
    datos_especificos: dict

@router.post("/login", response_model=dict)
async def login(request: LoginRequest):
    return controller.login(request.nombre_usuario, request.contrasena)

@router.get("/perfil", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(decode_access_token)):
    return controller.get_profile(current_user["usuario_id"], current_user["rol_id"])