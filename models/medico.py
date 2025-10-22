import psycopg2
from typing import List, Dict, Optional
from utils.db import db

class MedicoModel:
    def get_historial_medico(self, usuario_id: int, nombre: Optional[str] = None, identificacion: Optional[str] = None, fecha: Optional[str] = None, rango: Optional[str] = None) -> List[Dict]:
        """Obtiene el historial de citas atendidas por un médico."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT c.fecha_cita AS fecha, u2.nombre || ' ' || u2.apellido AS medico, c.hora_cita, 
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
        
    def registrar_atencion(self, paciente_id: int, medico_id: int, sintomas: str, diagnostico: str, recomendaciones: str) -> int:
        """Registra una atención médica."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                INSERT INTO historial_medico (cita_id, sistemas, diagnostico, recomendaciones)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """
                cursor.execute(query, (paciente_id, medico_id, diagnostico, recomendaciones))
                conn.commit()
            # Actualizar estado de la cita a 'Atendida' si existe
                cita_query = "UPDATE cita SET estado = 'Atendida' WHERE id = (SELECT cita_id FROM atencion WHERE id = %s)"
                cursor.execute(cita_query, (cursor.fetchone()["id"],))
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
    
