from inference_sdk import InferenceHTTPClient
import os
# 1. Define your RoboflowYOLO class
class RoboflowYOLO:
    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url=os.getenv("ROBOFLOW_API_URL"),
            api_key=os.getenv("ROBOFLOW_API_KEY")
        )
        self.workspace_name = os.getenv("ROBOFLOW_WORKSPACE_NAME")
        self.workflow_id = os.getenv("ROBOFLOW_WORKFLOW_ID")

    def run_inference(self, image_path: str, use_cache: bool = True):
        result = self.client.run_workflow(
            workspace_name=self.workspace_name,
            workflow_id=self.workflow_id,
            images={
                "image": image_path
            },
            use_cache=use_cache
        )
        if hasattr(result, 'json') and callable(result.json):
            return result.json()
        # Si ya es un dict, simplemente devuelve
        return result
    

    def parse_results(self, result: dict) -> dict:
        
        # 1. Adaptar el RESULTADO PRINCIPAL: Si es una lista, toma el primer elemento.
        if isinstance(result, list) and result:
            # Si 'result' es una lista con contenido, tomamos el primer elemento (el diccionario de resultados).
            image_result_dict = result[0]
        elif isinstance(result, dict):
            # Si 'result' es un diccionario (el formato anterior), lo usamos directamente.
            image_result_dict = result
        else:
            # Caso inesperado o vacío
            return {"detections": []}

        # 2. Ahora, usamos el diccionario 'image_result_dict' para obtener el contenedor de predicciones.
        # Esta línea ahora está segura porque 'image_result_dict' SIEMPRE será un dict (o vacío).
        image_result_container = image_result_dict.get("predictions")
        
        detections = []
        
        if image_result_container:
            
            # 3. Determinar la estructura interna (lista o diccionario)
            if isinstance(image_result_container, list) and image_result_container:
                # Caso A: El contenedor es una LISTA (doble anidación)
                detections = image_result_container[0].get("predictions", [])
                
            elif isinstance(image_result_container, dict):
                # Caso B: El contenedor es un DICCIONARIO
                detections = image_result_container.get("predictions", [])
                
        # 4. Procesar los resultados (Tu lógica original)
        parsed_results = []
        for detection in detections:
            parsed_results.append({
                "class": detection["class"],
                "confidence": detection["confidence"],
                "bounding_box": { 
                    "x": detection["x"],
                    "y": detection["y"],
                    "width": detection["width"],
                    "height": detection["height"]
                }
            })
            
        return {"detections": parsed_results}