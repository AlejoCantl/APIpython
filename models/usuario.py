import psycopg2
from typing import List, Optional, Dict, Any
from utils.db import db

class UsuarioModel:
    def authenticate(self, nombre_usuario: str, contrasena: str) -> Optional[Dict[str, Any]]:
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, rol_id, contrasena
                    FROM usuario
                    WHERE nombre_usuario = %s
                """, (nombre_usuario,))
                user = cursor.fetchone()
                return user if user and user["contrasena"] == contrasena else None
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def get_user_profile(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.nombre, u.apellido, u.correo, u.identificacion, r.nombre AS rol
                    FROM usuario u
                    JOIN rol r ON u.rol_id = r.id
                WHERE u.id = %s
            """, (usuario_id,))
            user_data = cursor.fetchone()
            return user_data
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def get_paciente_data(self, usuario_id: int) -> Dict:
        """Obtiene datos específicos del paciente."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT peso, altura, enfermedades, tipo_paciente
                    FROM paciente
                    WHERE usuario_id = %s
                """
                cursor.execute(query, (usuario_id,))
                paciente_data = cursor.fetchone() or {}
                return paciente_data
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def get_medico_data(self, usuario_id: int) -> Dict:
        """Obtiene datos específicos del médico."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT especialidad, consultorio
                    FROM medico
                    WHERE usuario_id = %s
                """
                cursor.execute(query, (usuario_id,))
                medico_data = cursor.fetchone() or {}
                return medico_data
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")
    
    def get_profesional_data(self, usuario_id: int) -> Dict:
        """Obtiene datos específicos del profesional de apoyo."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT area_expertise, disponibilidad
                    FROM profesional_apoyo
                    WHERE usuario_id = %s
                """
                cursor.execute(query, (usuario_id,))
                profesional_data = cursor.fetchone() or {}
                return profesional_data
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def get_citas_paciente(self, usuario_id: int) -> List[Dict]:
        """Obtiene las citas de un paciente."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT c.id, c.fecha, u.nombre || ' ' || u.apellido AS medico,
                           c.estado, c.motivo
                FROM cita c
                JOIN usuario u ON c.medico_id = u.id
                WHERE c.paciente_id = %s
            """
            cursor.execute(query, (usuario_id,))
            return cursor.fetchall()
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def get_ultima_cita(self, usuario_id: int) -> Dict:
        """Obtiene la fecha de la última cita de un paciente."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT fecha FROM cita WHERE paciente_id = %s ORDER BY fecha DESC LIMIT 1"
                cursor.execute(query, (usuario_id,))
                return cursor.fetchone() or {}
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def crear_cita(self, paciente_id: int, medico_id: int, fecha: str, motivo: str) -> int:
        """Crea una nueva cita pendiente de aprobación."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
            query = """
                INSERT INTO cita (paciente_id, medico_id, fecha, motivo, estado)
                VALUES (%s, %s, %s, %s, 'Pendiente')
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
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                SELECT c.id, c.fecha, u.nombre || ' ' || u.apellido AS paciente, c.motivo
                FROM cita c
                JOIN usuario u ON c.paciente_id = u.id
                WHERE c.estado = 'Pendiente'
            """
            cursor.execute(query)
            return cursor.fetchall()
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def aprobar_cita(self, cita_id: int, profesional_id: int) -> bool:
        """Aprueba una cita y actualiza el estado."""
        try:
            with db.get_connection() as conn:
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
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = "UPDATE cita SET estado = 'Rechazada', razon_rechazo = %s, profesional_id = %s WHERE id = %s"
                cursor.execute(query, (razon, profesional_id, cita_id))
                conn.commit()
                return cursor.rowcount > 0
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def get_historial_paciente(self, usuario_id: int, fecha: str | None = None, rango: str | None = None) -> List[Dict]:
        """Obtiene el historial de citas de un paciente."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT c.fecha, c.motivo, a.diagnostico, a.recomendaciones
                    FROM cita c
                LEFT JOIN atencion a ON c.id = a.cita_id
                WHERE c.paciente_id = %s AND c.estado = 'Atendida'
            """
                params = [usuario_id]
                if fecha:
                    query += " AND c.fecha = %s"
                    params.append(fecha)
                elif rango:
                    start, end = rango.split(" al ")
                    query += " AND c.fecha BETWEEN %s AND %s"
                    params.extend([start, end])
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def actualizar_datos_paciente(self, usuario_id: int, datos: dict) -> None:
        """Actualiza los datos específicos del paciente."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO paciente (usuario_id, peso, altura, enfermedades, tipo_paciente)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (usuario_id) DO UPDATE
                    SET peso = EXCLUDED.peso, altura = EXCLUDED.altura, 
                        enfermedades = EXCLUDED.enfermedades, tipo_paciente = EXCLUDED.tipo_paciente
                """
                cursor.execute(query, (usuario_id, datos["peso"], datos["altura"], datos["enfermedades"], datos.get("tipo_paciente", "Limitante")))
                result = cursor.commit()
                return result
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")

    def registrar_atencion(self, paciente_id: int, medico_id: int, sintomas: str, diagnostico: str, recomendaciones: str) -> int:
        """Registra una atención médica."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO atencion (paciente_id, medico_id, sintomas, diagnostico, recomendaciones)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """
                cursor.execute(query, (paciente_id, medico_id, sintomas, diagnostico, recomendaciones))
                conn.commit()
            # Actualizar estado de la cita a 'Atendida' si existe
                cita_query = "UPDATE cita SET estado = 'Atendida' WHERE id = (SELECT cita_id FROM atencion WHERE id = %s)"
                cursor.execute(cita_query, (cursor.fetchone()["id"],))
                conn.commit()
                return cursor.fetchone()["id"]
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")