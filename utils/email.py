import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración de SMTP (Mantenida)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", "no-reply@fundacionamigosninos.org")

# Constantes de estilo para reutilizar
COLOR_PRIMARIO = "#007bff"     # Azul brillante, profesional
COLOR_SECUNDARIO = "#f8f9fa"   # Gris muy claro para fondos de secciones
COLOR_EXITO = "#28a745"        # Verde para confirmaciones
COLOR_ALERTA = "#dc3545"       # Rojo para rechazos
COLOR_TEXTO = "#343a40"        # Texto oscuro para legibilidad


class EmailService:
    
    # --- Plantilla HTML Base para Evitar Repetición ---
    @staticmethod
    def _crear_body_html(paciente_nombre: str, titulo: str, subtitulo: str, color_titulo: str, 
                         color_fondo_recuadro: str, detalles_adicionales: str = "") -> str:
        
        # El HTML principal incluye la estructura base y los estilos en línea
        return f"""
        <html>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #e9ecef;">
            <div role="article" aria-label="Correo de Notificación de Cita Médica"
                 style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                
                <div class="header" style="background-color: {COLOR_PRIMARIO}; color: #ffffff; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">Fundación Amigos de los Niños</h1>
                </div>

                <div class="content-area" style="padding: 25px;">
                    <h2 style="color: {COLOR_TEXTO}; margin-top: 0;">¡Hola, {paciente_nombre}!</h2>
                    
                    <p style="font-size: 16px; color: {COLOR_TEXTO};">
                        Te informamos que tu cita médica ha sido <strong style="color: {color_titulo};">{titulo}</strong>.
                    </p>
                    
                    <div style="background-color: {color_fondo_recuadro}; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid {color_titulo};">
                        <h3 style="color: {COLOR_TEXTO}; margin-top: 0; margin-bottom: 15px;">Detalles de tu cita:</h3>
                        {subtitulo}
                        <ul style="list-style-type: none; padding: 0;">
                            {detalles_adicionales}
                        </ul>
                    </div>

                    <p style="font-size: 14px; color: {COLOR_TEXTO};">
                        Por favor, revisa los detalles. Si necesitas reprogramar, contáctanos con anticipación.
                    </p>
                </div>

                <div class="footer" style="background-color: {COLOR_SECUNDARIO}; color: {COLOR_TEXTO}; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px;">
                    <p style="margin: 0;"><strong>Fundación Amigos de los Niños</strong></p>
                    <p style="margin: 5px 0 0 0;">Cuidando la salud de quienes más lo necesitan. | <a href="#" style="color: {COLOR_PRIMARIO}; text-decoration: none;">Visítanos</a></p>
                </div>

            </div>
        </body>
        </html>
        """

    # --- Método Genérico para Enviar el Correo ---
    @staticmethod
    def _enviar(paciente_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = paciente_email
        
        # Solución al error de codificación: usar Header
        msg['Subject'] = Header(subject, 'utf-8').encode()
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, paciente_email, msg.as_string())
            server.quit()
            print(f"Correo enviado a {paciente_email} con asunto: {subject}")
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            raise Exception(f"No se pudo enviar el correo: {str(e)}")

    # ------------------------------------------------------------------
    # --- MÉTODOS PÚBLICOS UTILIZANDO LA PLANTILLA Y EL MÉTODO _enviar ---
    # ------------------------------------------------------------------

    @staticmethod
    def enviar_correo_confirmacion(paciente_email: str, paciente_nombre: str, medico_nombre: str, fecha: str, hora: str, especialidad: str):
        subject = "¡Tu cita ha sido aprobada!"
        
        detalles = f"""
            <li><strong style="color: {COLOR_TEXTO};">Médico:</strong> {medico_nombre}</li>
            <li><strong style="color: {COLOR_TEXTO};">Especialidad:</strong> {especialidad}</li>
            <li><strong style="color: {COLOR_TEXTO};">Fecha:</strong> {fecha}</li>
            <li><strong style="color: {COLOR_TEXTO};">Hora:</strong> {hora}</li>
        """
        
        body = EmailService._crear_body_html(
            paciente_nombre=paciente_nombre,
            titulo="APROBADA",
            subtitulo="", # No es necesario un subtitulo separado en este diseño
            color_titulo=COLOR_EXITO,
            color_fondo_recuadro="#e6ffed", # Verde claro para éxito
            detalles_adicionales=detalles
        )
        
        EmailService._enviar(paciente_email, subject, body)

    @staticmethod
    def enviar_correo_notificacion_cita_creada(paciente_email: str, paciente_nombre: str, medico_nombre: str, fecha: str, hora: str, especialidad: str):
        subject = "Confirmación: Tu cita ha sido creada"
        
        detalles = f"""
            <li><strong style="color: {COLOR_TEXTO};">Médico:</strong> {medico_nombre}</li>
            <li><strong style="color: {COLOR_TEXTO};">Especialidad:</strong> {especialidad}</li>
            <li><strong style="color: {COLOR_TEXTO};">Fecha:</strong> {fecha}</li>
            <li><strong style="color: {COLOR_TEXTO};">Hora:</strong> {hora}</li>
        """
        
        body = EmailService._crear_body_html(
            paciente_nombre=paciente_nombre,
            titulo="CREADA (Pendiente de Aprobación)",
            subtitulo="",
            color_titulo=COLOR_PRIMARIO,
            color_fondo_recuadro="#e6f4ff", # Azul claro suave
            detalles_adicionales=detalles
        )
        
        EmailService._enviar(paciente_email, subject, body)

    @staticmethod
    def enviar_correo_rechazo(paciente_email: str, paciente_nombre: str, medico_nombre: str, fecha: str, hora: str, especialidad: str, razon: str):
        subject = "Información importante sobre tu cita médica"
        
        detalles = f"""
            <li><strong style="color: {COLOR_TEXTO};">Médico:</strong> {medico_nombre}</li>
            <li><strong style="color: {COLOR_TEXTO};">Especialidad:</strong> {especialidad}</li>
            <li><strong style="color: {COLOR_TEXTO};">Fecha:</strong> {fecha}</li>
            <li><strong style="color: {COLOR_TEXTO};">Hora:</strong> {hora}</li>
            <li style="margin-top: 10px;"><strong>Razón del rechazo:</strong> <span style="color: {COLOR_ALERTA};">{razon}</span></li>
        """
        
        body = EmailService._crear_body_html(
            paciente_nombre=paciente_nombre,
            titulo="RECHAZADA",
            subtitulo="",
            color_titulo=COLOR_ALERTA,
            color_fondo_recuadro="#fff0f0", # Rojo claro suave para alerta
            detalles_adicionales=detalles
        )
        
        EmailService._enviar(paciente_email, subject, body)