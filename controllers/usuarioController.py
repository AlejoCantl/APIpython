from fastapi import HTTPException, status
from datetime import datetime, timedelta
from utils.auth import create_access_token  # Asegúrate de que esté importado
from models.usuario import UsuarioModel

class UsuarioController:
    def __init__(self):
        self.model = UsuarioModel()

    def login(self, nombre_usuario: str, contrasena: str) -> dict:
        user = self.model.authenticate(nombre_usuario, contrasena)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
        access_token = create_access_token(data={"sub": str(user["id"]), "rol_id": user["rol_id"]})
        return {"access_token": access_token, "token_type": "bearer"}

    def get_profile(self, usuario_id: int, rol_id: int) -> dict:
        user_data = self.model.get_user_profile(usuario_id, rol_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        datos_especificos = {}
        if user_data["rol_id"] == 1:  # Paciente
            datos_especificos = self.model.get_paciente_data(usuario_id) or {}
        elif user_data["rol_id"] == 2:  # Médico
            datos_especificos = self.model.get_medico_data(usuario_id) or {}
        elif user_data["rol_id"] == 3:  # Profesional de salud
            datos_especificos = self.model.get_profesional_data(usuario_id) or {}
        user_data["id"] = usuario_id  # ← ¡ESTO ES LO QUE FALTABA!
        user_data["datos_especificos"] = datos_especificos
        return user_data