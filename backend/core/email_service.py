"""
Email service for NavajaSuiza.
Sends formatted HTML emails to employees with their credentials.
"""
import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def build_welcome_html(first_name, email, password, login_url):
    """Build the HTML body for the welcome email."""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0; padding:0; background-color:#0f172a; font-family:'Segoe UI',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f172a; padding:40px 20px;">
            <tr>
                <td align="center">
                    <table width="560" cellpadding="0" cellspacing="0" style="background-color:#1e293b; border-radius:16px; border:1px solid rgba(99,102,241,0.2); overflow:hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #6366f1, #4f46e5); padding:32px; text-align:center;">
                                <h1 style="color:#ffffff; margin:0; font-size:24px; font-weight:700; letter-spacing:-0.5px;">
                                    🔧 NavajaSuiza
                                </h1>
                                <p style="color:rgba(255,255,255,0.8); margin:8px 0 0; font-size:14px;">
                                    Panel Empresarial
                                </p>
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding:32px;">
                                <h2 style="color:#e2e8f0; margin:0 0 8px; font-size:20px;">
                                    ¡Bienvenido/a, {first_name}!
                                </h2>
                                <p style="color:#94a3b8; margin:0 0 24px; font-size:15px; line-height:1.6;">
                                    El administrador te ha dado de alta en el sistema NavajaSuiza.
                                    A continuación encontrarás tus credenciales de acceso:
                                </p>

                                <!-- Credentials Card -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f172a; border-radius:12px; border:1px solid #334155; margin-bottom:24px;">
                                    <tr>
                                        <td style="padding:20px;">
                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="padding:8px 0;">
                                                        <span style="color:#94a3b8; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Usuario (Email)</span><br>
                                                        <span style="color:#818cf8; font-size:16px; font-weight:600;">{email}</span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding:8px 0; border-top:1px solid #1e293b;">
                                                        <span style="color:#94a3b8; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Contraseña</span><br>
                                                        <span style="color:#10b981; font-size:16px; font-weight:600; font-family:monospace;">{password}</span>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>

                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center">
                                            <a href="{login_url}"
                                               style="display:inline-block; padding:14px 32px; background:linear-gradient(135deg,#6366f1,#4f46e5); color:#ffffff; text-decoration:none; border-radius:12px; font-size:15px; font-weight:600; letter-spacing:0.3px;">
                                                Acceder a NavajaSuiza →
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding:20px 32px; border-top:1px solid #334155; text-align:center;">
                                <p style="color:#64748b; margin:0; font-size:12px;">
                                    ⚠️ Te recomendamos cambiar tu contraseña tras el primer acceso.
                                </p>
                                <p style="color:#475569; margin:8px 0 0; font-size:11px;">
                                    Este es un correo automático. No respondas a este mensaje.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def send_welcome_email(user, plain_password):
    """
    Send a welcome email with credentials to a newly created employee.

    Args:
        user: CustomUser instance (already saved)
        plain_password: The plaintext password to include in the email

    Returns:
        tuple: (success: bool, error_message: str | None)
    """
    login_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    subject = 'Bienvenido a NavajaSuiza - Tus Credenciales de Acceso'

    # Plain text fallback
    text_body = (
        f"Hola {user.first_name},\n\n"
        f"El administrador te ha dado de alta en NavajaSuiza.\n\n"
        f"Tus credenciales de acceso:\n"
        f"  Usuario (Email): {user.email}\n"
        f"  Contraseña: {plain_password}\n\n"
        f"Accede aquí: {login_url}\n\n"
        f"Te recomendamos cambiar tu contraseña tras el primer acceso.\n"
    )

    # HTML body
    html_body = build_welcome_html(
        first_name=user.first_name,
        email=user.email,
        password=plain_password,
        login_url=login_url,
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)

        logger.info(f'Welcome email sent to {user.email} ({user.empleado_id})')
        return True, None

    except SMTPException as e:
        error_msg = f'Error SMTP al enviar email a {user.email}: {str(e)}'
        logger.error(error_msg)
        return False, error_msg

    except Exception as e:
        error_msg = f'Error inesperado al enviar email a {user.email}: {str(e)}'
        logger.error(error_msg)
        return False, error_msg
