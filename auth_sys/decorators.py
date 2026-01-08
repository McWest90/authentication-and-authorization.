from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .utils import decode_jwt
from .models import CustomUser, Permission, Resource

def require_auth(resource_code=None, action=None):
    """
    resource_code: код ресурса (строка), к которому идет обращение
    action: действие 'create', 'read', 'update', 'delete'
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Получение токена
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = auth_header.split(' ')[1]
            
            try:
                # 2. Валидация токена
                payload = decode_jwt(token)
                user = CustomUser.objects.get(id=payload['id'])
                
                # 3. Проверка статуса пользователя
                if user.is_deleted:
                    return Response({'error': 'Account deleted'}, status=status.HTTP_401_UNAUTHORIZED)
                
                # Проверка Logout (токен был выпущен до последнего выхода)
                token_iat = payload.get('iat')
                if user.last_logout and token_iat:
                     last_logout_ts = user.last_logout.timestamp()
                     if token_iat < last_logout_ts:
                         return Response({'error': 'Session expired, please login again'}, status=status.HTTP_401_UNAUTHORIZED)

                # Сохраняем пользователя в request (как это делает Django)
                request.user_custom = user

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

            # 4. Проверка прав (Authorization), если указан ресурс
            if resource_code and action:
                # Если админ - пускаем везде (опционально)
                if user.role and user.role.slug == 'admin':
                    return view_func(request, *args, **kwargs)

                has_perm = False
                if user.role:
                    try:
                        perm = Permission.objects.get(role=user.role, resource__code=resource_code)
                        if action == 'read' and perm.can_read: has_perm = True
                        elif action == 'create' and perm.can_create: has_perm = True
                        elif action == 'update' and perm.can_update: has_perm = True
                        elif action == 'delete' and perm.can_delete: has_perm = True
                    except Permission.DoesNotExist:
                        pass
                
                if not has_perm:
                    return Response({'error': 'Forbidden: Insufficient rights'}, status=status.HTTP_403_FORBIDDEN)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator