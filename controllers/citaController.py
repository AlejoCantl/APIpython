from models.cita import CitaModel
from typing import Optional
from fastapi import HTTPException, UploadFile
from datetime import datetime, timedelta
import os
import shutil
import uuid
IMAGENES_DIR = "static/uploads/citas/"
class CitaController:
    def __init__(self):
        if not os.path.exists(IMAGENES_DIR):
            os.makedirs(IMAGENES_DIR)
        self.model = CitaModel()

    async def _guardar_imagen_en_disco(self, imagen: UploadFile) -> str:
        """Guarda la imagen en el disco con un nombre seguro y devuelve la ruta."""
        
        # 1. Generar nombre seguro
        ext = os.path.splitext(imagen.filename)[1] # Obtiene la extensión
        safe_filename = f"{uuid.uuid4()}{ext}"
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
            raise HTTPException(status_code=400, detail="Debe haber al menos 15 días entre citas")
        
        # 2. Crear Cita en BD y obtener cita_id
        # ⚠️ Asegúrate que self.model.crear_cita no espere 'motivo'
        cita_id = self.model.crear_cita(usuario_id, medico_id, fecha, hora, especialidad_id)
        
        # 3. Procesar y guardar las imágenes
        if imagenes:
            for imagen in imagenes:
                # Guardar en disco
                ruta_guardada = await self._guardar_imagen_en_disco(imagen)
                
                # Registrar en BD
                # ⚠️ Asumo que 'guardar_imagen_cita' registra la ruta en una tabla
                self.model.guardar_imagen_cita(cita_id, ruta_imagen=ruta_guardada) 
        
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
    
    def get_ultima_cita(self, usuario_id: int) -> dict:
        ultima_cita = self.model.get_ultima_cita(usuario_id)
        if not ultima_cita:
            raise HTTPException(status_code=204, detail="No hay última cita encontrada")
        return {"ultima_cita": ultima_cita}
    
    def get_especialidades(self) -> dict:
        especialidades = self.model.get_especialidades()
        return {"especialidades": especialidades}
    
    def get_medicos(self, especialidad_id: int) -> dict:
        medicos = self.model.get_medicos(especialidad_id)
        return {"medicos": medicos}
    
    