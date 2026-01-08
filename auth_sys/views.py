from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import CustomUser, Role, Permission, Resource
from .utils import hash_password, check_password, generate_jwt
from .decorators import require_auth

# --- МОДУЛЬ 1: Взаимодействие с пользователем ---

@api_view(['POST'])
def register(request):
    data = request.data
    if data['password'] != data['password_repeat']:
        return Response({'error': 'Passwords do not match'}, status=400)
    
    if CustomUser.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=400)

    # Присваиваем дефолтную роль (например, user)
    try:
        default_role = Role.objects.get(slug='user')
    except Role.DoesNotExist:
        default_role = None # Или создать

    hashed = hash_password(data['password'])
    user = CustomUser.objects.create(
        full_name=data['full_name'],
        email=data['email'],
        password_hash=hashed,
        role=default_role
    )
    return Response({'message': 'User registered', 'id': user.id}, status=201)

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=401)
    
    if user.is_deleted:
        return Response({'error': 'Account is deleted'}, status=401)

    if check_password(password, user.password_hash):
        token = generate_jwt(user.id)
        return Response({'token': token})
    else:
        return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['POST'])
@require_auth() # Только аутентификация
def logout(request):
    # При выходе обновляем метку времени. Все токены, выданные ДО, станут невалидны
    user = request.user_custom
    user.last_logout = timezone.now()
    user.save()
    return Response({'message': 'Logged out successfully'})

@api_view(['PATCH'])
@require_auth()
def update_profile(request):
    user = request.user_custom
    data = request.data
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    # Если меняем пароль
    if 'password' in data:
        user.password_hash = hash_password(data['password'])
        
    user.save()
    return Response({'message': 'Profile updated'})

@api_view(['DELETE'])
@require_auth()
def delete_account(request):
    user = request.user_custom
    user.is_deleted = True
    user.last_logout = timezone.now() # Сразу разлогиниваем
    user.save()
    return Response({'message': 'Account soft-deleted'})


# --- МОДУЛЬ 2: Управление правами (Админка) ---

@api_view(['POST'])
@require_auth() # В реальном коде здесь нужна проверка на роль Админа
def manage_permissions(request):
    # Упрощенный пример назначения прав
    # Пример body: {"role": "manager", "resource": "reports", "can_read": true}
    user = request.user_custom
    if not user.role or user.role.slug != 'admin':
        return Response({'error': 'Admins only'}, status=403)
        
    data = request.data
    role = Role.objects.get(slug=data['role'])
    resource, _ = Resource.objects.get_or_create(code=data['resource'])
    
    perm, _ = Permission.objects.get_or_create(role=role, resource=resource)
    
    if 'can_read' in data: perm.can_read = data['can_read']
    if 'can_create' in data: perm.can_create = data['can_create']
    # ... остальные поля
    perm.save()
    
    return Response({'message': 'Permissions updated'})


# --- МОДУЛЬ 3: Тестовые бизнес-объекты (Mock) ---

@api_view(['GET'])
@require_auth(resource_code='reports', action='read')
def get_reports(request):
    # Сюда попадет только тот, у кого роль имеет can_read=True для ресурса reports
    mock_data = [
        {'id': 1, 'title': 'Q1 Report', 'data': '...'},
        {'id': 2, 'title': 'Q2 Report', 'data': '...'},
    ]
    return Response(mock_data)

@api_view(['POST'])
@require_auth(resource_code='reports', action='create')
def create_report(request):
    return Response({'message': 'Report created!'}, status=201)