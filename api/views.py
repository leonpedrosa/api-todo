from django.core.validators import EmailValidator
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet, ViewSet, ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.mixins import *
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action, permission_classes
from rest_framework.authtoken.models import Token
from datetime import timedelta
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.models import *
from api.serializers import *
from api.utils import generate_password, send_password_email
from concurrent.futures import ThreadPoolExecutor

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Se o método for 'create', permitir qualquer usuário (sem autenticação)
        if self.action == 'create':
            return [AllowAny()]
        # Para outros métodos, exigir que o usuário esteja autenticado
        return [IsAuthenticated(), IsAdminUser()]


class AuthViewSet(ViewSet):
    @swagger_auto_schema(
        operation_summary='Login',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD)
            }
        ),
        responses={
            200: openapi.Response(
                description='',
                examples={
                    "application/json": {
                        "result": {
                            "user": "user@user.com",
                            "id": 1,
                            "token": "95595f53771b1da5ad881e6cc2d68e49f8dfb1d6"
                        }
                    }
                }
            ),
            401: openapi.Response(
                description='',
                examples={
                    "application/json": {
                        'result': {"error": "user not authorized"}
                    }
                }
            ),
            500: openapi.Response(
                description='',
                examples={
                    "application/json": {
                        'result': {"error": "unknown error 'MSG'"}
                    }
                }
            ),
        }
    )
    @action(methods=['post'], detail=False, url_path='login', permission_classes=[AllowAny])
    def login(self, request):
        if all([
            'username' in request.data,
            'password' in request.data
        ]):
            username = request.data['username']
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'result': {'error': 'user not authorized'}}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as error:
                return Response({'result': {'error': f'unknown error {str(error)}'}}, status=500)

            if user.check_password(request.data.get('password')):
                token, created = Token.objects.get_or_create(user=user)
                if token.created < timezone.now() + timedelta(days=-1):
                    token.delete()
                    token = Token.objects.create(user=user)
                return Response(
                    {
                        'result': {
                            'user': user.username,
                            'id': user.id,
                            'token': token.key,
                        }
                    }
                )
            else:
                return Response({'result': {'error': 'user not authorized'}}, status=401)

        else:
            return Response(
                {"result": {'error': f'Required fields missing username and password'}},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['post'], detail=False, url_path='logout')
    def logout(self, request):
        try:
            Token.objects.get(user=request.user).delete()
        except:
            pass

        return Response({"msg": "logged out"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            }
        )
    )
    @action(methods=['post'], detail=False, url_path='forgot', permission_classes=[AllowAny])
    def forgot_password(self, request):
        email = request.data.get('email', '')
        validator = EmailValidator()
        try:
            validator(email)
        except Exception as error:
            return Response({'result': {'error': str(error)}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            password = generate_password()
            user.set_password(password)
        except:
            return Response({'result': {'error': 'invalid email'}}, status=status.HTTP_400_BAD_REQUEST)

        # enviando email assincrono
        with ThreadPoolExecutor() as executor:
            executor.submit(send_password_email, user.email, password)

        return Response({"msg": "reset password with sucess"}, status=status.HTTP_200_OK)


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

