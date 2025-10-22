from models.medico import MedicoModel
from typing import Optional

class MedicoController:
    def __init__(self):
        self.model = MedicoModel()
    
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
    
    def actualizar_datos_especificos(self, usuario_id: int, datos: dict) -> dict:
        self.model.actualizar_datos_paciente(usuario_id, datos)
        return {"mensaje": "Datos actualizados con éxito"}