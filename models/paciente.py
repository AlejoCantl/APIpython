import psycopg2
from typing import List, Dict, Optional
from utils.db import db
import json

class PacienteModel:
    def get_citas_paciente(self, usuario_id: int) -> List[Dict]:
        """Obtiene las citas de un paciente."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                SELECT c.id, c.fecha_cita, c.hora_cita, u.nombre || ' ' || u.apellido AS medico,
                       c.estado, e.nombre AS especialidad
                FROM cita c
                JOIN usuario u ON c.usuario_medico_id = u.id
                JOIN especialidad e ON c.especialidad_id = e.id
                WHERE c.usuario_paciente_id = %s
                """
            cursor.execute(query, (usuario_id,))
            return cursor.fetchall()
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def get_proxima_cita(self, usuario_id: int) -> Dict:
        """Obtiene la próxima cita programada para un paciente."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                SELECT c.id, c.fecha_cita, c.hora_cita, u.nombre || ' ' || u.apellido AS medico, e.nombre AS especialidad, c.estado
                FROM cita c
                JOIN usuario u ON c.usuario_medico_id = u.id
                JOIN especialidad e ON c.especialidad_id = e.id
                WHERE c.usuario_paciente_id = %s AND c.estado = 'Aprobada' AND c.fecha_cita >= CURRENT_DATE
                ORDER BY c.fecha_cita ASC
                LIMIT 1
                """
            cursor.execute(query, (usuario_id,))
            return cursor.fetchone() or {}
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def get_ultima_cita(self, usuario_id: int) -> Dict:
        """Obtiene la fecha de la última cita de un paciente."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """SELECT c.fecha_cita AS fecha, u2.nombre || ' ' || u2.apellido AS medico, c.hora_cita, 
                           h.diagnostico, h.recomendaciones, h.sistema, e.nombre AS especialidad
                    FROM cita c
                    JOIN historial_medico h ON c.id = h.cita_id
                    JOIN especialidad e ON c.especialidad_id = e.id
                    JOIN usuario u ON c.usuario_paciente_id = u.id
                    JOIN usuario u2 ON c.usuario_medico_id = u2.id
                    WHERE c.estado = 'Atendida' AND c.usuario_paciente_id = %s
                    ORDER BY fecha DESC LIMIT 1"""
                cursor.execute(query, (usuario_id,))
                return cursor.fetchone() or {}
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def crear_cita(self, paciente_id: int, medico_id: int, fecha: str, hora: str, especialidad_id: int) -> Dict:
        """Crea una nueva cita pendiente de aprobación."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
            query = """
                INSERT INTO cita (usuario_paciente_id, usuario_medico_id, especialidad_id, fecha_cita, hora_cita, estado)
                VALUES (%s, %s, %s, %s, %s, 'Pendiente')
                RETURNING id
                """
            cursor.execute(query, (paciente_id, medico_id, especialidad_id, fecha, hora))
            conn.commit()
            return cursor.fetchone()["id"]
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def guardar_imagen_cita(self, cita_id: int, ruta_imagen: str, resultado_yolo: dict, tipo_subida: str = "Paciente") -> int:
        """Guarda una imagen asociada a una cita."""
        try:
            resultado_yolo_json = json.dumps(resultado_yolo)
            with db.get_connection_context() as conn:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO imagen_cita (cita_id, ruta_imagen, resultado_yolo, tipo_subida)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """
                    cursor.execute(query, (cita_id, ruta_imagen, resultado_yolo_json, tipo_subida))
                    conn.commit()
                    imagen_id = cursor.fetchone()["id"]
                    return imagen_id
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        

    def get_historial_paciente(self, usuario_id: int, fecha: Optional[str] = None, rango: Optional[str] = None) -> List[Dict]:
        """Obtiene el historial de citas de un paciente."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT c.fecha_cita AS fecha, u2.nombre || ' ' || u2.apellido AS medico, c.hora_cita, 
                           h.diagnostico, h.recomendaciones, h.sistema, e.nombre AS especialidad
                    FROM cita c
                    JOIN historial_medico h ON c.id = h.cita_id
                    JOIN especialidad e ON c.especialidad_id = e.id
                    JOIN usuario u ON c.usuario_paciente_id = u.id
                    JOIN usuario u2 ON c.usuario_medico_id = u2.id
                    WHERE c.estado = 'Atendida' AND c.usuario_paciente_id = %s
                """
                params = [usuario_id]
                if fecha and not rango:
                    query += " AND c.fecha_cita = %s"
                    params.append(fecha)
                elif rango and not fecha:
                    start, end = rango.split(" al ")
                    query += " AND c.fecha_cita BETWEEN %s AND %s"
                    params.extend([start, end])
                else:
                    if fecha and rango:
                        raise ValueError("No se pueden usar 'fecha' y 'rango' simultáneamente")
                query += " ORDER BY c.fecha_cita DESC"
                print(f"Query (paciente): {query}")
                print(f"Params (paciente): {params}")
                cursor.execute(query, params)
                result = cursor.fetchall()
                print(f"Result (paciente): {result}")
                return result
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        except ValueError as e:
            raise Exception(f"Error en los parámetros: {e}")
    
    def get_especialidades(self) -> List[Dict]:
        """Obtiene la lista de especialidades médicas."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = "SELECT id, nombre FROM especialidad"
                cursor.execute(query)
                return cursor.fetchall()
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def get_medicos(self , especialidad_id: int) -> List[Dict]:
        """Obtiene la lista de médicos."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                SELECT u.id, u.nombre || ' ' || u.apellido AS nombre_completo
                FROM medico m
                JOIN usuario u ON m.medico_id = u.id
                JOIN especialidad e ON m.especialidad_id = e.id
                WHERE m.especialidad_id = %s
                """
                cursor.execute(query, (especialidad_id,))
                return cursor.fetchall()
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def get_datos_cita_para_correo(self, cita_id: int) -> Dict:
        """
        Devuelve todos los datos necesarios para enviar cualquier correo relacionado con la cita.
        """
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        c.fecha_cita AS fecha, c.hora_cita AS hora,
                        p.correo AS paciente_correo,
                        p.nombre AS paciente_nombre,
                        p.apellido AS paciente_apellido,
                        m.nombre || ' ' || m.apellido AS medico_nombre,
                        e.nombre AS especialidad
                    FROM cita c
                    JOIN usuario p ON c.usuario_paciente_id = p.id
                    JOIN usuario m ON c.usuario_medico_id = m.id
                    JOIN especialidad e ON c.especialidad_id = e.id
                    WHERE c.id = %s
                """
                cursor.execute(query, (cita_id,))
                result = cursor.fetchone()
                if not result:
                    return {}
                
                return {
                    "paciente_email": result["paciente_correo"],
                    "paciente_nombre": f"{result['paciente_nombre']} {result['paciente_apellido']}".strip(),
                    "medico_nombre": result["medico_nombre"],
                    "fecha": result["fecha"].strftime("%Y-%m-%d"),
                    "hora": result["hora"],
                    "especialidad": result["especialidad"]
                }
        except Exception as e:
            print(f"Error en get_datos_cita_para_correo: {e}")
            return {}