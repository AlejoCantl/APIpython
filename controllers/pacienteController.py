from models.paciente import PacienteModel
from typing import Optional
from fastapi import HTTPException, UploadFile
from datetime import datetime, timedelta
import os
import shutil
from utils.yolo_roboflow import RoboflowYOLO
#from utils.yolo_local import LocalYOLO
from utils.email import EmailService

IMAGENES_DIR = "static/uploads/citas/"
class PacienteController:
    def __init__(self):
        if not os.path.exists(IMAGENES_DIR):
            os.makedirs(IMAGENES_DIR)
        self.model = PacienteModel()
        self.yolo = RoboflowYOLO()

    async def _guardar_imagen_en_disco(self, imagen: UploadFile) -> str:
        """Guarda la imagen en el disco con un nombre seguro y devuelve la ruta."""
        
        # 1. Generar nombre seguro
        safe_filename = f"{imagen.filename}"
        file_location = os.path.join(IMAGENES_DIR, safe_filename)
        
        # 2. Guardar eficientemente
        try:
            # Usar shutil.copyfileobj para copiar el stream del archivo
            with open(file_location, "wb") as buffer:
                # El .file es el objeto de archivo temporal que se debe copiar
                shutil.copyfileobj(imagen.file, buffer)
        except Exception as e:
            # Puedes manejar errores de disco aquí
            print(f"Error al guardar el archivo: {e}")
            raise HTTPException(status_code=500, detail="Error al guardar la imagen en el servidor")
        
        return file_location # Devuelve la ruta donde se guardó

    def get_citas_paciente(self, usuario_id: int) -> dict:
        citas = self.model.get_citas_paciente(usuario_id)
        return {"citas": citas}
    
    def get_proxima_cita(self, usuario_id: int) -> dict:
        proxima_cita = self.model.get_proxima_cita(usuario_id)
        if not proxima_cita:
            raise HTTPException(status_code=204, detail="No hay próxima cita encontrada")
        return {"proxima_cita": proxima_cita}
    
    def get_ultima_cita(self, usuario_id: int) -> dict:
        ultima_cita = self.model.get_ultima_cita(usuario_id)
        if not ultima_cita:
            raise HTTPException(status_code=204, detail="No hay última cita encontrada")
        return {"ultima_cita": ultima_cita}
    
    async def crear_cita(
        self, 
        usuario_id: int, 
        medico_id: int, 
        fecha: str, 
        hora: str, 
        especialidad_id: int, 
        imagenes: list[UploadFile]
    ) -> dict:
        
        # 1. Validación de Cita (la que ya tenías)
        ultima_cita = self.model.get_ultima_cita(usuario_id)
        if ultima_cita and (datetime.fromisoformat(fecha).date() - ultima_cita["fecha"]) < timedelta(days=15):
            raise HTTPException(status_code=400, detail="Debe haber al menos 15 días entre citas.")
        
        # 2. Crear Cita en BD y obtener cita_id
        # ⚠️ Asegúrate que self.model.crear_cita devuelve el ID de la cita creada
        cita_id = self.model.crear_cita(usuario_id, medico_id, fecha, hora, especialidad_id)
        # 3. Procesar y guardar las imágenes
        if imagenes:
            for imagen in imagenes:
                # Guardar en disco
                ruta_guardada = await self._guardar_imagen_en_disco(imagen)
                result_yolo = self.yolo.run_inference(image_path=ruta_guardada)
                print(f"Resultado YOLO para {ruta_guardada}: {result_yolo}")
                # Parsear resultados
                result_yolo = self.yolo.parse_results(result_yolo)
                # Registrar en BD
                # ⚠️ Asumo que 'guardar_imagen_cita' registra la ruta en una tabla
                self.model.guardar_imagen_cita(cita_id, ruta_imagen=ruta_guardada, resultado_yolo=result_yolo) 

        # 4. Enviar correo de notificación
        cita_datos = self.model.get_datos_cita_para_correo(cita_id)
        paciente_email = cita_datos["paciente_email"]
        if paciente_email:
            try:
                EmailService.enviar_correo_notificacion_cita_creada(
                    paciente_email=paciente_email,
                    paciente_nombre=cita_datos["paciente_nombre"],
                    medico_nombre=cita_datos["medico_nombre"],
                    fecha=cita_datos["fecha"],
                    hora=cita_datos["hora"],
                    especialidad=cita_datos["especialidad"]
                )
            except Exception as e:
                print(f"Error al enviar correo de nueva cita: {e}")
                # No fallamos la creación si falla el correo
                pass
        return {"mensaje": "Cita pendiente de aprobación", "cita_id": cita_id}
    
    def get_historial_paciente(self, usuario_id: int, fecha: Optional[str] = None, rango: Optional[str] = None) -> dict:
        historial = self.model.get_historial_paciente(usuario_id, fecha, rango)
        return {"historial": historial}
    
    def get_especialidades(self) -> dict:
        especialidades = self.model.get_especialidades()
        return {"especialidades": especialidades}
    
    def get_medicos(self, especialidad_id: int) -> dict:
        medicos = self.model.get_medicos(especialidad_id)
        return {"medicos": medicos}
