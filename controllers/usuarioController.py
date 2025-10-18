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
        access_token = create_access_token(data={"sub": user["id"], "rol_id": user["rol_id"]})
        return {"access_token": access_token, "token_type": "bearer"}

    def get_profile(self, usuario_id: int, rol_id: int) -> dict:
        user_data = self.model.get_user_profile(usuario_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        datos_especificos = {}
        if user_data["rol_id"] == 1:  # Administrador
            datos_especificos = self.model.get_paciente_data(usuario_id) or {}
        elif user_data["rol_id"] == 2:  # Médico
            datos_especificos = self.model.get_medico_data(usuario_id) or {}
        elif user_data["rol_id"] == 3:  # Profesional de apoyo
            datos_especificos = self.model.get_profesional_data(usuario_id) or {}
        user_data["datos_especificos"] = datos_especificos
        return user_data

    def get_citas_paciente(self, usuario_id: int) -> dict:
        citas = self.model.get_citas_paciente(usuario_id)
        return {"citas": citas}

    def crear_cita(self, usuario_id: int, medico_id: int, fecha: str, motivo: str) -> dict:
        ultima_cita = self.model.get_ultima_cita(usuario_id)
        if ultima_cita and (datetime.fromisoformat(fecha) - ultima_cita["fecha"]) < timedelta(days=15):
            raise HTTPException(status_code=400, detail="Debe haber al menos 15 días entre citas")
        cita_id = self.model.crear_cita(usuario_id, medico_id, fecha, motivo)
        return {"mensaje": "Cita pendiente de aprobación", "cita_id": cita_id}

    def get_historial_paciente(self, usuario_id: int, fecha: str | None = None, rango: str | None = None) -> dict:
        historial = self.model.get_historial_paciente(usuario_id, fecha, rango)
        return {"historial": historial}

    def actualizar_datos_especificos(self, usuario_id: int, datos: dict) -> dict:
        self.model.actualizar_datos_paciente(usuario_id, datos)
        return {"mensaje": "Datos actualizados con éxito"}

    def get_citas_profesional(self) -> dict:
        citas = self.model.get_citas_pendientes()
        return {"citas": citas}

    def aprobar_cita(self, cita_id: int, aprobado: bool, razon: str | None, profesional_id: int) -> dict:
        if aprobado:
            self.model.aprobar_cita(cita_id, profesional_id)
            # Implementar envío de correo
            return {"mensaje": "Cita aprobada"}
        else:
            self.model.rechazar_cita(cita_id, razon, profesional_id)
            return {"mensaje": "Cita rechazada", "razon": razon}

    def get_historial_medico(self, paciente_id: int) -> dict:
        historial = self.model.get_historial_paciente(paciente_id)
        return {"historial": historial}

    def registrar_atencion(self, paciente_id: int, medico_id: int, sintomas: str, diagnostico: str, recomendaciones: str) -> dict:
        atencion_id = self.model.registrar_atencion(paciente_id, medico_id, sintomas, diagnostico, recomendaciones)
        return {"mensaje": "Atención registrada", "atencion_id": atencion_id}