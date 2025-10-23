from models.profesionalSalud import ProfesionalSaludModel
from fastapi import HTTPException
from utils.email import EmailService

class ProfesionalSaludController:
    def __init__(self):
        self.model = ProfesionalSaludModel()

    def get_citas_profesional(self) -> dict:
        citas = self.model.get_citas_pendientes()
        return {"citas": citas}
    
    def aprobar_cita(self, cita_id: int, aprobado: bool, razon: str | None, profesional_id: int) -> dict:
        cita_detalle = self.model.get_detalle_cita(cita_id)
        if not cita_detalle:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        paciente_email = cita_detalle["correo"]
        paciente_nombre = f"{cita_detalle['nombre']} {cita_detalle['apellido']}"
        medico_nombre = cita_detalle["medico"]
        fecha = cita_detalle["fecha"]
        hora = cita_detalle["hora"]
        especialidad = cita_detalle["especialidad"]
        if aprobado:
            self.model.aprobar_cita(cita_id, profesional_id)
            # Implementar envío de correo
            if not paciente_email:
                print("Advertencia: No se encontró correo del paciente")
            else:
                try:
                    EmailService.enviar_correo_confirmacion(
                        paciente_email=paciente_email,
                        paciente_nombre=paciente_nombre or "Paciente",
                        medico_nombre=medico_nombre,
                        fecha=fecha,
                        hora=hora,
                        especialidad=especialidad
                    )
                except Exception as e:
                    print(f"Error al enviar correo: {e}")
                    # No fallamos la aprobación si falla el correo
                    pass
            return {"mensaje": "Cita aprobada"}
        else:
            self.model.rechazar_cita(cita_id, razon, profesional_id)
            # Implementar envío de correo de rechazo
            if not paciente_email:
                print("Advertencia: No se encontró correo del paciente")
            else:
                try:
                    EmailService.enviar_correo_rechazo(
                        paciente_email=paciente_email,
                        paciente_nombre=paciente_nombre or "Paciente",
                        medico_nombre=medico_nombre,
                        fecha=fecha,
                        hora=hora,
                        especialidad=especialidad,
                        razon=razon
                    )
                except Exception as e:
                    print(f"Error al enviar correo de rechazo: {e}")
                    # No fallamos el rechazo si falla el correo
                    pass
            return {"mensaje": "Cita rechazada", "razon": razon}
        
    def get_detalle_cita(self, cita_id: int) -> dict:
        detalles = self.model.get_detalle_cita(cita_id)
        return {"detalle_cita": detalles}


