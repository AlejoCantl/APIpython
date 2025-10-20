from models.cita import CitaModel
from typing import Optional
from fastapi import HTTPException
from datetime import datetime, timedelta

class CitaController:
    def __init__(self):
        self.model = CitaModel()
    
    def get_citas_paciente(self, usuario_id: int) -> dict:
        citas = self.model.get_citas_paciente(usuario_id)
        return {"citas": citas}

    def get_proxima_cita(self, usuario_id: int) -> dict:
        proxima_cita = self.model.get_proxima_cita(usuario_id)
        if not proxima_cita:
            raise HTTPException(status_code=204, detail="No hay próxima cita encontrada")
        return {"proxima_cita": proxima_cita}

    def crear_cita(self, usuario_id: int, medico_id: int, fecha: str, motivo: str) -> dict:
        ultima_cita = self.model.get_ultima_cita(usuario_id)
        if ultima_cita and (datetime.fromisoformat(fecha) - ultima_cita["fecha"]) < timedelta(days=15):
            raise HTTPException(status_code=400, detail="Debe haber al menos 15 días entre citas")
        cita_id = self.model.crear_cita(usuario_id, medico_id, fecha, motivo)
        return {"mensaje": "Cita pendiente de aprobación", "cita_id": cita_id}

    def get_historial_paciente(self, usuario_id: int, fecha: Optional[str] = None, rango: Optional[str] = None) -> dict:
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

    def get_historial_medico(self, nombre: Optional[str] = None, identificacion: Optional[str] = None, usuario_id: Optional[int] = None, fecha: Optional[str] = None, rango: Optional[str] = None) -> dict:
        historial = self.model.get_historial_medico(nombre, identificacion, usuario_id, fecha, rango)
        #for item in historial:
            #doc_diag = nlp(item["diagnostico"] or "")
            #doc_rec = nlp(item["recomendaciones"] or "")
            #item["diagnostico_tokens"] = [token.text for token in doc_diag]
            #item["recomendaciones_entidades"] = [(ent.text, ent.label_) for ent in doc_rec.ents]
        return {"historial": historial}

    def registrar_atencion(self, paciente_id: int, medico_id: int, sintomas: str, diagnostico: str, recomendaciones: str) -> dict:
        atencion_id = self.model.registrar_atencion(paciente_id, medico_id, sintomas, diagnostico, recomendaciones)
        return {"mensaje": "Atención registrada", "atencion_id": atencion_id}

    def get_detalle_cita(self, cita_id: int) -> dict:
        detalles = self.model.get_detalle_cita(cita_id)
        return {"detalle_cita": detalles}