from models.profesionalSalud import ProfesionalSaludModel

class ProfesionalSaludController:
    def __init__(self):
        self.model = ProfesionalSaludModel()

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
        
    def get_detalle_cita(self, cita_id: int) -> dict:
        detalles = self.model.get_detalle_cita(cita_id)
        return {"detalle_cita": detalles}


