from rest_framework import status
from rest_framework.response import Response
import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

def format_response(data=None, message=None, status_code=status.HTTP_200_OK, errors=None, success=True):
    """
    Formats the response to follow a standard REST API structure, including a success flag.
    
    Arguments:
    - data: The data to return in the response (optional)
    - message: The message to return in the response (optional)
    - status_code: The HTTP status code to return (default is 200 OK)
    - errors: Errors to include in the response if there are any (optional)
    - success: A boolean flag indicating whether the operation was successful or not (default is True)
    
    Returns:
    - A Response object formatted in a standard way.
    """
    response_data = {
        'success': success,  # Flag indicating success or failure
    }

    if errors:
        response_data['errors'] = errors  # Include errors if present
    elif data:
        response_data['data'] = data  # Include data if present
    
    if message:
        response_data['message'] = message  # Include a message if present

    return Response(response_data, status=status_code)  # Return the formatted response


def generate_verification_token():
    return secrets.token_urlsafe(32)

def is_token_expired(created_at):
    if not created_at:
        return True
    return timezone.now() > created_at + timedelta(days=1)


def send_verification_email(email, token):
    subject = "Verify your email"
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    message = f"Please click the following link to verify your email: {verification_url}"
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )