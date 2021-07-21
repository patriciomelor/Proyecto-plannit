from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.utils.html import strip_tags
# CONFIGURACION PARA ENVIO DE CORREO PARA UMBRAL DOCUMENTOS ATRASADOS

def send_email(html, context, subject, recipients):
    """
    Función pre-cargada con las configuraciones y valores necesarios para ser enviado.
    Se le puede pasar:
        - html: HTML que se enviará.
        - context: Información a ingresar dentro del html (para renderizar).
        - subject: Asunto especifico para el correo.
        - recipients: Receptores de los correos notificativos.
    """
    connection = get_connection()
    html_content = render_to_string(html, context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject= subject,
        body= text_content,
        from_email= settings.EMAIL_HOST_USER,
        to= list(recipients),
        connection=connection
    )
    email.attach_alternative(html_content, "text/html")
    email.send