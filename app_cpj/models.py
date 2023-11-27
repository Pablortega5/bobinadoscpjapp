from django.db import models
from django.contrib.auth.models import AbstractUser, Permission


class Sucursal(models.Model):
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre
    
class ArchivoPDF(models.Model):
    
    archivo = models.FileField(upload_to='pdfs/')
    
class Guias(models.Model):
    nombre = models.CharField(max_length=50)
    
    direccion = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT)  
    presupuesto = models.TextField(max_length=100)
    valor_presupuesto = models.IntegerField() 
    abono = models.IntegerField()   
    saldo = models.IntegerField()  
    total = models.IntegerField()  
    f_registro = models.DateTimeField(auto_now_add=True, null=True)
    archivo_pdf = models.ForeignKey(ArchivoPDF, on_delete=models.SET_NULL, blank=True, null=True)
    estado_pago =models.CharField(max_length=20, default="Pendiente",choices=[("Pendiente","Pendiente" ),("Completado", "Completado")],)
    estado = models.CharField(
        max_length=20, default="En Proceso",
        choices=[("En Proceso","En Proceso" ), ("Listo", "Listo"), ("Completado", "Completado")],
    )

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=12, unique=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(max_length=255)

    def __str__(self):
        return self.nombre



class CustomUser(AbstractUser):
    telefono = models.CharField(max_length=15)
    

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='custom_users',
        verbose_name='Grupos',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='custom_users',
        verbose_name='Permisos',
    )



class Comentario(models.Model):
    autor = models.CharField(max_length=100)
    contenido = models.TextField()
    calificacion = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.autor 



