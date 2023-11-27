from django.urls import path
from .import views


urlpatterns = [ 
    path('index', views.index, name='index'),
    path('', views.home, name='home'),
    path('listar_guias', views.listar_guias, name= "listar_guias"),
    path('actualizar/<id>/', views.actualizar, name= "actualizar"),
    path('crear_guia', views.crear_guia, name= "crear_guia"),
    path('eliminar/<id>/', views.eliminar, name= "eliminar"),
    path('registrar_usuario/',views.registro, name = "registrar_usuario"),
    path('usuarios/', views.listar_usuarios, name='usuarios'),
    path('usuarios/cambiar_grupos_permisos/<int:user_id>/', views.cambiar_grupos_permisos, name='cambiar_grupos_permisos'),
    path('eliminar_usuario/<id>/', views.eliminar_usuario, name= "eliminar_usuario"),
    path('editar_usuario/<id>/', views.editar_usuario, name= "editar_usuario"),
    path('registrar_cliente/',views.registrar_cliente, name = "registrar_cliente"),
    path('listar_clientes', views.listar_clientes, name= "listar_clientes"),
    path('editar_cliente/<id>/', views.editar_cliente, name= "editar_cliente"),
    path('eliminar_cliente/<id>/', views.eliminar_cliente, name= "eliminar_cliente"),
    path('obtener_cliente/<int:cliente_id>/', views.obtener_datos_cliente, name='obtener_cliente'),
    path('factura/<int:guia_id>/generar_pdf/', views.generar_factura_pdf, name='generar_factura_pdf'),
    path('crear_guia_y_enviar_factura/<int:id>/', views.generar_factura_pdf_y_enviar_email, name='crear_guia_y_enviar_factura'),
    path('realizar_pago/<int:guia_id>/', views.realizar_pago, name='realizar_pago'),
    path('retorno_webpay/', views.retorno_webpay, name='retorno_webpay'),
    path('generar_factura_pdf/<int:guia_id>/', views.generar_factura_pdf, name='generar_factura_pdf'),
    path('cambiar_contrasena/', views.cambiar_contraseña, name='cambiar_contraseña'),
  
    
    
    
    
    
    ]