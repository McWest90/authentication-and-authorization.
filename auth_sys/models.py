from django.db import models
from django.utils import timezone

class Role(models.Model):
    slug = models.CharField(max_length=50, unique=True)  # admin, user
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.slug

class Resource(models.Model):
    code = models.CharField(max_length=50, unique=True) # reports, users
    description = models.CharField(max_length=255, blank=True)

class Permission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    
    # Флаги действий (CRUD)
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'resource')

class CustomUser(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)  # Храним хеш, не пароль!
    
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    
    is_deleted = models.BooleanField(default=False) # Мягкое удаление
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Для реализации Logout (инвалидация токенов, выпущенных до этого времени)
    last_logout = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email