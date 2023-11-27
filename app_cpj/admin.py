from django.contrib import admin
from .models import Comentario, Sucursal, Guias

admin.site.register(Guias)
admin.site.register(Sucursal)
admin.site.register(Comentario)
