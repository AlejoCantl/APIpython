import psycopg2
from typing import List, Dict, Optional
from utils.db import db
import json

class MedicoModel:
    def get_historial_medico(self, usuario_id: int, nombre: Optional[str] = None, identificacion: Optional[str] = None, fecha: Optional[str] = None, rango: Optional[str] = None) -> List[Dict]:
        """Obtiene el historial de citas atendidas por un médico."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT c.fecha_cita AS fecha, c.hora_cita, 
                           h.diagnostico, h.recomendaciones, h.sistema, e.nombre AS especialidad,
                           u.nombre || ' ' || u.apellido AS paciente
                    FROM cita c
                    JOIN historial_medico h ON c.id = h.cita_id
                    JOIN especialidad e ON c.especialidad_id = e.id
                    JOIN usuario u ON c.usuario_paciente_id = u.id
                    JOIN usuario u2 ON c.usuario_medico_id = u2.id
                    WHERE c.estado = 'Atendida' AND c.usuario_medico_id = %s
                """
                params = [usuario_id]
                if fecha and not rango:
                    query += " AND c.fecha_cita = %s"
                    params.append(fecha)
                elif rango and not fecha:
                    start, end = rango.split(" al ")
                    query += " AND c.fecha_cita BETWEEN %s AND %s"
                    params.extend([start, end])
                if nombre:
                    query += " AND (u.nombre ILIKE %s OR u.apellido ILIKE %s)"
                    params.extend([f"%{nombre}%", f"%{nombre}%"])
                if identificacion:
                    query += " AND u.identificacion = %s"
                    params.append(identificacion)
                query += " ORDER BY c.fecha_cita DESC"
                print(f"Query (medico): {query}")
                print(f"Params (medico): {params}")
                cursor.execute(query, params)
                result = cursor.fetchall()
                print(f"Result (medico): {result}")
                return result
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        except ValueError as e:
            raise Exception(f"Error en los parámetros: {e}")
        
    def registrar_atencion(self, cita_id: int, sistema: str, diagnostico: str, recomendaciones: str) -> int:
        """Registra una atención médica."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                INSERT INTO historial_medico (cita_id, sistema, diagnostico, recomendaciones)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """
                cursor.execute(query, (cita_id, sistema, diagnostico, recomendaciones))
                conn.commit()
                return cursor.fetchone()["id"]
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def actualizar_datos_paciente(self, usuario_id: int, datos: dict) -> None:
        """Actualiza los datos específicos del paciente."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO paciente (usuario_id, peso, altura, enfermedades, tipo_paciente)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (usuario_id) DO UPDATE
                    SET peso = EXCLUDED.peso, altura = EXCLUDED.altura, 
                        enfermedades = EXCLUDED.enfermedades, tipo_paciente = EXCLUDED.tipo_paciente
                    """
                cursor.execute(query, (usuario_id, datos["peso"], datos["altura"], datos["enfermedades"], datos.get("tipo_paciente", "Limitante")))
                result = conn.commit()
                return result
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")


    def get_cita_pacientes_aprobadas(self, medico_id: int) -> List[Dict]:
        """Obtiene las citas aprobadas para un médico."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT c.id AS cita_id, c.fecha_cita, c.hora_cita, u.nombre || ' ' || u.apellido AS paciente,
                           e.nombre AS especialidad
                    FROM cita c
                    JOIN usuario u ON c.usuario_paciente_id = u.id
                    JOIN especialidad e ON c.especialidad_id = e.id
                    WHERE c.usuario_medico_id = %s AND c.estado = 'Aprobada'
                    ORDER BY c.fecha_cita ASC
                """
                cursor.execute(query, (medico_id,))
                result = cursor.fetchall()
                return result
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
    
    def actualizar_estado_cita(self, cita_id: int, estado: str):
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = "UPDATE cita SET estado = %s WHERE id = %s"
                cursor.execute(query, (estado, cita_id))
                conn.commit()
        except psycopg2.Error as e:
            raise Exception(f"Error al actualizar estado: {e}")
        
    def get_paciente_info(self, paciente_id: int) -> Dict:
        """Obtiene la información de un paciente."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT u.nombre, u.apellido, u.correo, u.identificacion, p.peso, p.altura, p.enfermedades, p.tipo_paciente
                    FROM usuario u
                    LEFT JOIN paciente p ON u.id = p.usuario_id
                    WHERE u.id = %s
                """
                cursor.execute(query, (paciente_id,))
                result = cursor.fetchone()
                if not result:
                    raise Exception("Paciente no encontrado")
                return result
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def guardar_imagen_atencion(self, cita_id: int, ruta_imagen: str, resultado_yolo: dict, tipo_subida: str) -> None:
        """Guarda la información de una imagen asociada a una atención médica."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO imagen_cita (cita_id, ruta_imagen, resultado_yolo, tipo_subida)
                    VALUES (%s, %s, %s, %s)
                """
                json_resultado = json.dumps(resultado_yolo)
                cursor.execute(query, (cita_id, ruta_imagen, json_resultado, tipo_subida))
                conn.commit()
        except psycopg2.Error as e:
            raise Exception(f"Error al guardar imagen de atención: {e}")