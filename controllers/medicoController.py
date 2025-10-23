from models.medico import MedicoModel
from typing import Optional
from utils.yolo_roboflow import RoboflowYOLO
from fastapi import HTTPException
import os
import shutil
#from utils.nlp import nlp  # Asegúrate de que esté importado si

class MedicoController:
    def __init__(self):
        self.model = MedicoModel()
        self.model = RoboflowYOLO()
    
    def get_historial_medico(self, nombre: Optional[str] = None, identificacion: Optional[str] = None, usuario_id: Optional[int] = None, fecha: Optional[str] = None, rango: Optional[str] = None) -> dict:
        historial = self.model.get_historial_medico(nombre, identificacion, usuario_id, fecha, rango)
        #for item in historial:
            #doc_diag = nlp(item["diagnostico"] or "")
            #doc_rec = nlp(item["recomendaciones"] or "")
            #item["diagnostico_tokens"] = [token.text for token in doc_diag]
            #item["recomendaciones_entidades"] = [(ent.text, ent.label_) for ent in doc_rec.ents]
        return {"historial": historial}
    
    def registrar_atencion(self, paciente_id: int, medico_id: int, sintomas: str, diagnostico: str, recomendaciones: str, imagenes: list = []) -> dict:
        yolo = RoboflowYOLO()
        resultados_yolo = []
        for imagen in imagenes:
            ruta = self._guardar_imagen(imagen)
            result = yolo.run_inference(image_path=ruta)
            parsed = yolo.parse_results(result)
            resultados_yolo.append({"ruta": ruta, "resultado": parsed})
            # Opcional: guardar en imagen_cita aquí
        atencion_id = self.model.registrar_atencion(paciente_id, medico_id, sintomas, diagnostico, recomendaciones)
        return {"mensaje": "Atención registrada", "atencion_id": atencion_id, "resultados_yolo": resultados_yolo}
    
    def actualizar_datos_especificos(self, usuario_id: int, datos: dict) -> dict:
        self.model.actualizar_datos_paciente(usuario_id, datos)
        return {"mensaje": "Datos actualizados con éxito"}
    
    def _guardar_imagen(self, imagen) -> str:
        # Similar a pacienteController
        safe_name = f"atencion_{imagen.filename}"
        path = os.path.join("static/uploads/atenciones/", safe_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            shutil.copyfileobj(imagen.file, f)
        return path