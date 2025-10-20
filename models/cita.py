import psycopg2
from typing import List, Dict, Optional
from utils.db import db

class CitaModel:
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

    def crear_cita(self, paciente_id: int, medico_id: int, fecha: str, motivo: str) -> int:
        """Crea una nueva cita pendiente de aprobación."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
            query = """
                INSERT INTO cita (usuario_paciente_id, usuario_medico_id, especialidad_id, fecha_cita, hora_cita, estado)
                VALUES (%s, %s, %s, %s, %s, 'Pendiente')
                RETURNING id
                """
            cursor.execute(query, (paciente_id, medico_id, fecha, motivo))
            conn.commit()
            return cursor.fetchone()["id"]
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def get_citas_pendientes(self) -> List[Dict]:
        """Obtiene todas las citas pendientes para el profesional de la salud."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                SELECT c.id, c.fecha_cita AS fecha, u.nombre || ' ' || u.apellido AS paciente
                FROM cita c
                JOIN usuario u ON c.usuario_paciente_id = u.id
                WHERE c.estado = 'Pendiente'
                """
            cursor.execute(query)
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

    def aprobar_cita(self, cita_id: int, profesional_id: int) -> bool:
        """Aprueba una cita y actualiza el estado."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = "UPDATE cita SET estado = 'Aprobada', profesional_id = %s WHERE id = %s"
                cursor.execute(query, (profesional_id, cita_id))
                conn.commit()
                return cursor.rowcount > 0
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
        
    def rechazar_cita(self, cita_id: int, razon: str, profesional_id: int) -> bool:
        """Rechaza una cita con una razón."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = "UPDATE cita SET estado = 'Rechazada', razon_rechazo = %s, profesional_id = %s WHERE id = %s"
                cursor.execute(query, (razon, profesional_id, cita_id))
                conn.commit()
                return cursor.rowcount > 0
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
        
    def get_detalle_cita(self, cita_id: int) -> Dict:
        """Obtiene el detalle de una cita específica."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                SELECT u.nombre, u.apellido, u.correo, u.identificacion, u.direccion, u.ciudad, u.pais,
                    p.tipo_paciente, p.peso, p.altura, p.enfermedades
                FROM cita c
                JOIN usuario u ON c.usuario_paciente_id = u.id
                JOIN paciente p ON u.id = p.usuario_id
                WHERE c.id = %s
                """
            cursor.execute(query, (cita_id,))
            return cursor.fetchone() or {}
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")