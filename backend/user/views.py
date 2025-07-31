from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from secrets import token_urlsafe
from django.core.mail import send_mail
from django.conf import settings

from .models import Credentials
from functions.auth_functions import token_generator, auth_check, send_verification_email

import logging
import hashlib
import threading

logger = logging.getLogger(__name__)

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        try:
            existing_user = Credentials.objects.filter(
                Q(username=request.data['username']) | Q(email=request.data['email'])
            ).first()
            if existing_user:
                return JsonResponse({'msg': 'User already exists'},
                                    status=status.HTTP_400_BAD_REQUEST)
            if request.data['password'] != request.data['confirmPassword']:
                return JsonResponse({'msg': 'Passwords do not match'},
                                    status=status.HTTP_400_BAD_REQUEST)
            password = hashlib.sha256(request.data['password'].encode()).hexdigest()
            new_user = Credentials.objects.create(
                username=request.data['username'],
                email=request.data['email'],
                password=password,
                verification_code=1234
            )
            new_user.save()
            threading.Thread(target=send_verification_email, args=(
                new_user.email, new_user.verification_code)).start()
            return JsonResponse({'msg': 'User registered successfully'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during registration: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def verification(request):
    if request.method == 'PATCH':
        try:
            user = Credentials.objects.filter(email=request.data['email']).first()
            if str(request.data['verificationCode']) == str(user.verification_code):
                user.is_verified = True
                user.save()
                return JsonResponse({'msg': 'User verified successfully'},
                                        status=status.HTTP_200_OK)
            else:
                return JsonResponse({'msg': 'Invalid verification code'},
                                        status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error during verification: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def login(request):
    if request.method == 'PATCH':
        try:
            try:
                user = Credentials.objects.get(email=request.data['email'])
            except Credentials.DoesNotExist:
                return JsonResponse({'msg': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            if not user.is_verified:
                return JsonResponse({'msg': 'User not verified'},
                                    status=status.HTTP_401_UNAUTHORIZED)
            if not user.is_active:
                return JsonResponse({'msg': 'User is inactive'},
                                    status=status.HTTP_403_FORBIDDEN)
            correct_password = hashlib.sha256(request.data['password'].encode(
                )).hexdigest() == user.password
            if not correct_password:
                return JsonResponse({'msg': 'Incorrect password'},
                                    status=status.HTTP_401_UNAUTHORIZED)
            else:
                user.last_login = timezone.now()
                token = token_generator(user.username, user.email)
                return JsonResponse({'token': token, 'msg': 'Logged in successfully'},
                                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PATCH'])
def logout(request):
    if request.method == 'PATCH':
        try:
                response = Response()
                response.delete_cookie('token')
                response['message'] = 'Logged out successfully'
                response.status_code = status.HTTP_200_OK
                return response
        except Exception as e:
            logging.error(f"Error during logout: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def change_password(request):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            old_password = hashlib.sha256(request.data['oldPassword'].encode()).hexdigest()
            if old_password != user.password:
                return JsonResponse({'message': 'Incorrect old password'},
                                    status=status.HTTP_401_UNAUTHORIZED)
            if request.data['newPassword'] != request.data['confirmPassword']:
                return JsonResponse({'message': 'Passwords do not match'},
                                    status=status.HTTP_400_BAD_REQUEST)
            new_password = hashlib.sha256(request.data['newPassword'].encode()).hexdigest()
            user.password = new_password
            user.save()
            return JsonResponse({'message': 'Password changed successfully'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video upload: {str(e)}")
            return JsonResponse({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def forgot_password(request):
    if request.method == 'PATCH':
        try:
            user = Credentials.objects.filter(email=request.data['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            new_password = token_urlsafe(8)  
            new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            user.password = new_password_hash
            user.save()
            subject = 'Password Reset'
            message = f'Your new password is: {new_password}, feel free to login to your account. You can change your password from the my profile section.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, email_from, recipient_list) 
            return JsonResponse({'message': 'Password reset successfully'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video upload: {str(e)}")
            return JsonResponse({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def resend_verification(request):
    if request.method == 'PATCH':
        try:
            user = Credentials.objects.filter(email=request.data['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                subject = 'Verification Code'
                message = f'Your verification code is: {user.verification_code}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email]
                send_mail(subject, message, email_from, recipient_list)
                return JsonResponse({'message': 'Verification code sent successfully'},
                                    status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during verification code resend: {str(e)}")
            return JsonResponse({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        