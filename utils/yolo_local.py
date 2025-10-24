from ultralytics import YOLO
import os
from dotenv import load_dotenv

load_dotenv()

class LocalYOLO:
    """
    Adaptador para usar YOLO local (Ultralytics) con la misma interfaz que RoboflowYOLO.
    Drop-in replacement para RoboflowYOLO.
    """
    def __init__(self, model_path: str = None):
        """
        Inicializa el modelo YOLO local.
        
        Args:
            model_path: Ruta al archivo .pt del modelo entrenado.
                       Si no se proporciona, usa la variable de entorno YOLO_MODEL_PATH
        """
        # Obtener ruta del modelo desde parámetro o variable de entorno
        self.model_path = model_path or os.getenv("YOLO_MODEL_PATH", "best.pt")
        
        # Cargar el modelo YOLO
        try:
            self.model = YOLO(self.model_path)
            print(f"[LocalYOLO] Modelo cargado exitosamente desde: {self.model_path}")
        except Exception as e:
            print(f"[LocalYOLO] Error al cargar el modelo: {e}")
            raise Exception(f"No se pudo cargar el modelo YOLO desde {self.model_path}")

    def run_inference(self, image_path: str, use_cache: bool = True, conf: float = 0.25):
        """
        Ejecuta inferencia en una imagen.
        
        Args:
            image_path: Ruta a la imagen
            use_cache: Parámetro de compatibilidad (no usado en YOLO local)
            conf: Umbral de confianza mínimo (default: 0.25)
            
        Returns:
            Resultados de la predicción en formato compatible con parse_results
        """
        try:
            # Ejecutar predicción
            results = self.model.predict(
                source=image_path,
                conf=conf,
                verbose=False  # Evitar logs excesivos
            )
            
            # Retornar el primer resultado (una imagen)
            return results[0] if results else None
            
        except Exception as e:
            print(f"[LocalYOLO] Error en inferencia: {e}")
            return None

    def parse_results(self, result) -> dict:
        """
        Parsea los resultados de YOLO local al mismo formato que Roboflow.
        
        Args:
            result: Objeto Results de Ultralytics YOLO
            
        Returns:
            Dict con formato: {"detections": [{"class": str, "confidence": float, "bounding_box": {...}}]}
        """
        if result is None:
            return {"detections": []}
        
        detections = []
        
        # Iterar sobre las detecciones
        for box in result.boxes:
            # Extraer información de cada detección
            class_id = int(box.cls[0])  # ID de la clase
            class_name = result.names[class_id]  # Nombre de la clase
            confidence = float(box.conf[0])  # Confianza
            
            # Coordenadas en formato xywh (centro x, centro y, ancho, alto)
            xywh = box.xywh[0].tolist()
            x, y, w, h = xywh
            
            # Agregar detección en formato compatible con Roboflow
            detections.append({
                "class": class_name,
                "confidence": confidence,
                "bounding_box": {
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                }
            })
        
        return {"detections": detections}
