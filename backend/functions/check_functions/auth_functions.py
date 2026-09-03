from django.http import JsonResponse
from rest_framework import status
from django.core.mail import send_mail

import jwt

from core.settings import SECRET_KEY
from user.models import Credentials, AdminCredentials

from django.conf import settings


def token_generator(username, email):
    payload = {
        'username': username,
        'email': email
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def auth_check(token):
    if not token:
        return {'error': JsonResponse({'message': 'Invalid or missing token'},
                                      status=status.HTTP_403_FORBIDDEN)}
    try:
        payload = jwt.decode(token,
                             SECRET_KEY,
                             algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'error': JsonResponse({'message': 'Token expired'},
                                      status=status.HTTP_403_FORBIDDEN)}
    
    user = Credentials.objects.filter(username=payload['username'],
                                      email=payload['email']).first()
    if not user:
        return {'error': JsonResponse({'message': 'User not found'},
                                      status=status.HTTP_404_NOT_FOUND)}
    return {'user': user}

def send_verification_email(email, verification_code):
    subject = 'Verification Code'
    message = f'Your verification code is: {verification_code}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    
def admin_token_generator(username, email, admin_code):
    payload = {
        'username': username,
        'email': email,
        'admin_code': admin_code
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def admin_auth_check(token):
    if not token:
        return {'error': JsonResponse({'message': 'Invalid or missing token'},
                                      status=status.HTTP_403_FORBIDDEN)}
    try:
        payload = jwt.decode(token,
                             SECRET_KEY,
                             algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'error': JsonResponse({'message': 'Token expired'},
                                      status=status.HTTP_403_FORBIDDEN)}
    
    user = AdminCredentials.objects.filter(
        admin_username=payload['username'],
        admin_email=payload['email'],
        admin_code=payload['admin_code']
    ).first()
    
    if not user:
        return {'error': JsonResponse({'message': 'Admin user not found'},
                                      status=status.HTTP_404_NOT_FOUND)}
    return {'user': user}