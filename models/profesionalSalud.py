import psycopg2
from typing import List, Dict
from utils.db import db

class ProfesionalSaludModel:
    def get_citas_pendientes(self) -> List[Dict]:
        """Obtiene todas las citas pendientes para el profesional de la salud."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                SELECT c.id, c.fecha_cita AS fecha, u.nombre || ' ' || u.apellido AS paciente, u.identificacion, c.hora_cita as hora, u2.nombre || ' ' || u2.apellido AS medico, e.nombre AS especialidad
                FROM cita c
                JOIN usuario u ON c.usuario_paciente_id = u.id
                JOIN usuario u2 ON c.usuario_medico_id = u2.id
                JOIN especialidad e ON c.especialidad_id = e.id
                WHERE c.estado = 'Pendiente'
                """
            cursor.execute(query)
            return cursor.fetchall()
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
        
    def get_detalle_cita(self, cita_id: int) -> Dict:
        """Obtiene el detalle de una cita específica."""
        try:
            with db.get_connection_context() as conn:
                cursor = conn.cursor()
                query = """
                SELECT u.nombre, u.apellido, u.correo, u.identificacion, u.direccion, u.ciudad, u.pais,
                    p.tipo_paciente, p.peso, p.talla, p.enfermedades, c.fecha_cita as fecha, c.hora_cita as hora, e.nombre AS especialidad,
                    u2.nombre || ' ' || u2.apellido AS medico
                FROM cita c
                JOIN usuario u ON c.usuario_paciente_id = u.id
                JOIN usuario u2 ON c.usuario_medico_id = u2.id
                JOIN paciente p ON u.id = p.usuario_id
                JOIN especialidad e ON c.especialidad_id = e.id
                WHERE c.id = %s
                """
            cursor.execute(query, (cita_id,))
            return cursor.fetchone() or {}
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")