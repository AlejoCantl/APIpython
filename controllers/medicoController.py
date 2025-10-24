from models.medico import MedicoModel
from typing import Dict, Optional
from utils.yolo_roboflow import RoboflowYOLO
#from utils.yolo_local import LocalYOLO
from fastapi import HTTPException
import os
import shutil
#from utils.nlp import nlp  # Asegúrate de que esté importado si

class MedicoController:
    def __init__(self):
        self.model = MedicoModel()
        self.yolo = RoboflowYOLO()

    def get_historial_medico(self, usuario_id: Optional[int] = None, nombre: Optional[str] = None, identificacion: Optional[str] = None, fecha: Optional[str] = None, rango: Optional[str] = None) -> dict:
        historial = self.model.get_historial_medico(
            usuario_id=usuario_id,
            nombre=nombre, 
            identificacion=identificacion, 
            fecha=fecha, 
            rango=rango
        )        #for item in historial:
            #doc_diag = nlp(item["diagnostico"] or "")
            #doc_rec = nlp(item["recomendaciones"] or "")
            #item["diagnostico_tokens"] = [token.text for token in doc_diag]
            #item["recomendaciones_entidades"] = [(ent.text, ent.label_) for ent in doc_rec.ents]
        return {"historial": historial}
    
# CAMBIO: Recibir cita_id en lugar de paciente_id. Mantenemos medico_id.
    def registrar_atencion(self, cita_id: int, sistema: str, diagnostico: str, recomendaciones: str, imagenes: list = []) -> dict:
        
        # Lógica de YOLO (permanece igual)
        resultados_yolo = []

        for imagen in imagenes:
            ruta = self._guardar_imagen(imagen)
            result = self.yolo.run_inference(image_path=ruta)
            parsed = self.yolo.parse_results(result)
            resultados_yolo.append({"resultado": parsed})
            
        # 1. Registrar la atención en historial_medico
        # CAMBIO: Llamar al modelo pasando cita_id
        atencion_id = self.model.registrar_atencion(cita_id, sistema, diagnostico, recomendaciones)

        # 2. Actualizar el estado de la CITA a 'Atendida'
        # CAMBIO: Usar cita_id y el estado 'Atendida'
        self.model.actualizar_estado_cita(cita_id, "Atendida")
        
        # 3. Guardar resultados de YOLO (permanece igual)
        for resultado in resultados_yolo:
            self.model.guardar_imagen_atencion(atencion_id, ruta, resultado["resultado"], tipo_subida="Médico")

        return {"mensaje": "Atención registrada y cita actualizada a 'Atendida'", "atencion_id": atencion_id, "cita_id": cita_id, "detections": [r["resultado"]["detections"] for r in resultados_yolo]}
    
    def actualizar_datos_especificos(self, usuario_id: int, datos: dict) -> dict:
        self.model.actualizar_datos_paciente(usuario_id, datos)
        return {"mensaje": "Datos actualizados con éxito"}
    
    def _guardar_imagen(self, imagen) -> str:
        # Similar a pacienteController
        safe_name = f"{imagen.filename}"
        path = os.path.join("static/uploads/atenciones/", safe_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            shutil.copyfileobj(imagen.file, f)
        return path

    def get_paciente_citas_aprobadas(self, usuario_id: int) -> dict:
        citas = self.model.get_cita_pacientes_aprobadas(usuario_id)
        return {"citas_aprobadas": citas}
    
    def get_paciente_info(self, paciente_id: int) -> Dict:
        return self.model.get_paciente_info(paciente_id)
    
