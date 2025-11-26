from django.db import models
from django.conf import settings

class Alumno(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alumnos')
    nombre = models.CharField(max_length=150)
    curso = models.CharField(max_length=100)
    email = models.EmailField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.curso}"
