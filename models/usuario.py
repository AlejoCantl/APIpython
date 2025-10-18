import psycopg2
from typing import Optional, Dict, Any
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

    def get_user_profile(self, usuario_id: int, rol_id: int) -> Optional[Dict[str, Any]]:
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
            user_data["rol_id"] = rol_id  # Añadir rol_id para uso posterior
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
                    SELECT cargo, fecha_ingreso
                    FROM profesional_salud
                    WHERE usuario_id = %s
                """
                cursor.execute(query, (usuario_id,))
                profesional_data = cursor.fetchone() or {}
                return profesional_data
        except psycopg2.Error as e:
            raise Exception(f"Error en la base de datos: {e}")