from io import BytesIO
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .models import ArchivoPDF, Cliente, Comentario, Guias, Sucursal
from .forms import ComentarioForm, CustomUserCreationForm, GuiaForm, ClienteForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login
from django.template.loader import get_template
from weasyprint import HTML, CSS
from proyecto_cpj import settings
from proyecto_cpj.wsgi import *
from django.db.models import Sum,F
import calendar
from django.utils import timezone
from datetime import datetime
import json
from django.db.models.functions import ExtractMonth
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from django.core.files.base import ContentFile
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
TEMPLATES_DIRS = (
    'os.path.join(BASE_DIR,"templates")'
)



# Diccionario de nombres de meses en español
meses_espanol = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}

# Diccionario de nombres de días de la semana y meses en español
dias_semana = {
    0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"
}
@login_required
def obtener_datos_cliente(request, cliente_id):
    
    cliente = Cliente.objects.get(pk=cliente_id)
    data = {
        'nombre': cliente.nombre,
        'direccion': cliente.direccion,
        'correo': cliente.correo,
        'telefono': cliente.telefono,
        # Agrega otros campos según sea necesario
    }
    return JsonResponse(data)
@login_required
def index(request):
    # Obtener la fecha actual
    now = timezone.now()

    # Obtener el año actual
    ano_actual = datetime.now().year
    fecha_actual = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Obtener el primer y último día del mes actual
    first_day = now.replace(day=1)
    last_day = now.replace(day=calendar.monthrange(now.year, now.month)[1])
    
    # Calcular la suma total de los totales de las guías para el mes actual
    suma_total = Guias.objects.filter(f_registro__date__range=[first_day, last_day]).aggregate(total=Sum('total'))['total']
    
    # Calcular la suma de IVA por sucursal para el mes actual
    suma_iva_por_sucursal = Guias.objects.filter(f_registro__date__range=[first_day, last_day]).values('sucursal__nombre').annotate(iva=Sum(F('valor_presupuesto') * 0.19))
    
    # Filtra las guías creadas en el día actual
    guias_del_dia = Guias.objects.filter(f_registro__date=fecha_actual.date())

    # Filtrar las instancias de Guias para el año actual
    guias_del_ano = Guias.objects.filter(f_registro__year=ano_actual)

    # Calcula la suma de totales por sucursal para el día actual
    suma_por_sucursal = guias_del_dia.values('sucursal__nombre').annotate(total=Sum('total'))

    # Calcular la suma de los totales mensuales
    totales_mensuales = Guias.objects.filter(f_registro__year=ano_actual).annotate(mes=ExtractMonth('f_registro')).values('mes').annotate(total_mensual=Sum('total')).order_by('mes')

    # Calcula la suma total de los totales de las guías para el día actual
    suma_totales_dia = guias_del_dia.aggregate(Sum('total'))['total__sum'] or 0

     # Calcular la suma total de los valores de IVA para el mes actual (19% del valor_presupuesto)
    suma_iva = Guias.objects.filter(f_registro__date__range=[first_day, last_day]).aggregate(iva=Sum(F('valor_presupuesto') * 0.19))['iva']

    # Convertir QuerySet a lista de diccionarios y luego serializar a JSON
    totales_mensuales_json = json.dumps(list(totales_mensuales))
   
    # Obtener el nombre del mes actual en español
    nombre_dia = dias_semana[now.weekday()]
    nombre_mes = meses_espanol[now.month]
    sucursales = [item['sucursal__nombre'] for item in suma_por_sucursal]
    totales = [item['total'] for item in suma_por_sucursal]

    # Obtén las etiquetas (nombres de sucursal) y los datos (sumas de IVA)
    iva_labels = [item['sucursal__nombre'] for item in suma_iva_por_sucursal]
    iva_data = [item['iva'] for item in suma_iva_por_sucursal]
   
   # Obtén la suma de totales por sucursal
    suma_totales = Guias.objects.values('sucursal__nombre').annotate(total_sum=Sum('total'))
    labels = [suma['sucursal__nombre'] for suma in suma_totales]
    data = [suma['total_sum'] for suma in suma_totales]     
    
    # Renderizar la plantilla con los datos
    return render(request, 'index.html', {
        'suma_total': suma_total,
        'nombre_dia': nombre_dia,
        'suma_iva': suma_iva,
        'nombre_mes': nombre_mes,
        'labels': labels,
        'data': data,
        'sucursales': sucursales,
        'totales': totales,
        'iva_labels': iva_labels,
        'iva_data': iva_data,
        'suma_totales_dia': suma_totales_dia,
        'totales_mensuales': totales_mensuales_json,
    })



@login_required
def listar_guias(request):
    query = request.GET.get('q')

    if query:
        try:
            guias = Guias.objects.filter(Q(id__icontains=int(query))).order_by('-f_registro')
        except ValueError:
            guias = Guias.objects.none()
    else:
        guias = Guias.objects.all().order_by('-f_registro')

    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(guias, 10)
        guias = paginator.page(page)
    except EmptyPage as e:
        raise Http404(f'Página solicitada está fuera de rango: {e.message}')
    except PageNotAnInteger:
        guias = paginator.page(1)

    data = {
        'entity': guias,
        'paginator': paginator,
        'query': query,
    }
    return render(request, "crud_guias/listar.html", data)
@login_required
def actualizar(request, id):
    
    guia = get_object_or_404(Guias, id=id)

    data = {
         'form' : GuiaForm(instance = guia)
    }

    if request.method == 'POST':
         formulario = GuiaForm(data=request.POST, instance=guia)
         if formulario.is_valid():
              formulario.save()
              messages.success(request, "Actualizado correctamente")
              return redirect (to="listar_guias")
         data["form"] = formulario

    return render (request, "crud_guias/actualizar.html", data)

@permission_required('app_cpj.delete_cliente')
def eliminar(request, id):
    guia = get_object_or_404(Guias, id=id)
    guia.delete()
    messages.success(request, "Eliminado correctamente")
    return redirect(to="listar_guias")

@login_required
def crear_guia(request):
        data = {
             'form': GuiaForm()
        }
        if request.method == 'POST':
            formulario = GuiaForm(data=request.POST)
            if formulario.is_valid():
                  formulario.save()
                  messages.success(request, "Guia Creada")
                  return redirect (to="listar_guias")
            else:
                data["form"]= formulario

        return render(request, "crud_guias/crear.html", data)

@login_required
def registro(request):
     data = {
          'form': CustomUserCreationForm()
     }

     if request.method == 'POST':
          formulario = CustomUserCreationForm(data=request.POST)
          if formulario.is_valid():
               formulario.save()
               user = authenticate(username=formulario.cleaned_data["username"], password = formulario.cleaned_data["password1"] )
               messages.success(request, "Registro completado")
               return redirect (to="usuarios")
          else:
            data["form"] = formulario

     return render (request, 'registration/registro.html', data)



@permission_required('app_cpj.add_user')
def listar_usuarios(request):
    # Obtener la lista de usuarios ordenados por id
    usuarios = User.objects.all().order_by('id')
    page = request.GET.get('page',1)
    # Obtener todos los grupos de permisos disponibles
    grupos_permisos = Group.objects.all()

    try:
         paginator = Paginator(usuarios, 10)
         guias = paginator.page(page)
    except:
         raise Http404

    if request.method == 'POST':
        # Procesar el formulario cuando se envía
        usuario_id = request.POST.get('usuario_id')
        grupo_seleccionado_id = request.POST.get('grupo_permisos')

        try:
            usuario = User.objects.get(id=usuario_id)
            grupo_seleccionado = Group.objects.get(id=grupo_seleccionado_id)
            usuario.groups.set([grupo_seleccionado])
            messages.success(request, f'Grupo de permisos asignado con éxito a {usuario.username}')
        except User.DoesNotExist or Group.DoesNotExist:
            messages.error(request, 'Error al asignar el grupo de permisos.')

        return redirect('usuarios')  # Redirigir a la misma página después de procesar el formulario

    # Crear un diccionario con los datos que se pasarán al template
    data = {
        'entity': usuarios,
        'paginator': paginator,
        'grupos_permisos': grupos_permisos,
    }

    # Renderizar el template y pasar los datos
    return render(request, "registration/list.html", data)



@permission_required('app_cpj.add_user')
def cambiar_grupos_permisos(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        selected_groups = request.POST.getlist('grupos')

      
        user.groups.clear()

        
        for group_name in selected_groups:
            group = get_object_or_404(Group, name=group_name)
            user.groups.add(group)

        return redirect('usuarios')  

    # Obtén la lista de todos los grupos
    grupos = Group.objects.all()

    return render(request, 'your_template.html', {'user': user, 'grupos': grupos})

@permission_required('app_cpj.add_user')
def eliminar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    usuario.delete()
    messages.success(request, "Eliminado correctamente")
    return redirect(to="usuarios")

@permission_required('app_cpj.add_user')
def editar_usuario(request, id):
    
    usuario = get_object_or_404(User, id=id)

    data = {
         'form' : CustomUserCreationForm(instance = usuario)
    }

    if request.method == 'POST':
         formulario = CustomUserCreationForm(data=request.POST, instance=usuario)
         if formulario.is_valid():
              formulario.save()
              messages.success(request, "Actualizado correctamente")
              return redirect (to="usuarios")
         data["form"] = formulario

    return render (request, "registration/actualizar_usuario.html", data)

@login_required
def registrar_cliente(request):
     data = {
             'form': ClienteForm()
        }
     if request.method == 'POST':
        formulario = ClienteForm(data=request.POST)
        if formulario.is_valid():
           formulario.save()
           messages.success(request, "Cliente Registrado")         
           return redirect('listar_clientes')  
        else:
          data["form"]= formulario
    
     return render(request, 'crud_clientes/registrar_cliente.html', data)

@login_required
def listar_clientes(request):
    clientes = Cliente.objects.all().order_by('id')
    page = request.GET.get('page',1)

    try:
         paginator = Paginator(clientes, 10)
         clientes = paginator.page(page)
    except:
         raise Http404

    data = {
         'entity' : clientes,
         'paginator': paginator
    }
    return render (request, "crud_clientes/listar_clientes.html", data)


@login_required
def editar_cliente(request, id):
    
    cliente = get_object_or_404(Cliente, id=id)

    data = {
         'form' : ClienteForm(instance = cliente)
    }

    if request.method == 'POST':
         formulario = ClienteForm(data=request.POST, instance=cliente)
         if formulario.is_valid():
              formulario.save()
              messages.success(request, "Actualizado correctamente")
              return redirect (to="listar_clientes")
         data["form"] = formulario

    return render (request, "crud_clientes/actualizar_cliente.html", data)

@permission_required('app_cpj.delete_cliente')
def eliminar_cliente(request, id):
    usuario = get_object_or_404(Cliente, id=id)
    usuario.delete()
    messages.success(request, "Eliminado correctamente")
    return redirect(to="listar_clientes")


@login_required
def generar_factura_pdf(request, guia_id):
    guia = get_object_or_404(Guias, id=guia_id)

    # Cargar la plantilla HTML
    template = get_template('factura.html')

    # Renderizar la plantilla HTML con los datos de la guía
    html = template.render({'guia': guia})

    # Crear un archivo PDF a partir del HTML
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=factura_{guia_id}.pdf'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response



@login_required
def generar_factura_pdf_y_enviar_email(request, id):
    guia = get_object_or_404(Guias, id=id)

    # Cargar la plantilla HTML
    template = get_template('factura.html')

    # Renderizar la plantilla HTML con los datos de la guía
    html = template.render({'guia': guia})

    # Crear un archivo PDF a partir del HTML
    pdf_content = BytesIO()
    pdf_response = HttpResponse(content_type='application/pdf')
    pdf_response['Content-Disposition'] = f'attachment; filename=factura_{id}.pdf'

    pisa_status = pisa.CreatePDF(html, dest=pdf_content)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    # Guardar el PDF en el modelo ArchivoPDF
    archivo_pdf = ArchivoPDF()
    archivo_pdf.guia = guia
    archivo_pdf.archivo.save(f'factura_{id}.pdf', ContentFile(pdf_content.getvalue()))

    # Enviar el correo electrónico con el PDF adjunto
    to_email = guia.correo
    subject = 'Factura de servicio'
    message = 'Adjunto encontrarás la factura correspondiente a tu servicio. Gracias por tu preferencia.'
    from_email = settings.DEFAULT_FROM_EMAIL

    email = EmailMessage(subject, message, from_email, [to_email])
    email.attach(f'factura_{id}.pdf', pdf_content.getvalue(), 'application/pdf')
    email.send()

    messages.success(request, "Correo enviado")

    return redirect('listar_guias')



def home(request):
    comentarios = Comentario.objects.all()
    guia_resultado = None


    if request.method == 'POST':
        id_ingresado = request.POST.get('id', '')  # Asegúrate de tener un campo de formulario con name="id"
        try:
            id_ingresado = int(id_ingresado)
            guia_resultado = Guias.objects.get(id=id_ingresado)
        except (ValueError, Guias.DoesNotExist):
            guia_resultado = None
    else:
        guia_resultado = None
    
    if request.method == 'POST':
        formulario = ComentarioForm(data=request.POST)
        if formulario.is_valid():
                formulario.save()
                return redirect (to="home")

    data = {
        'form': ComentarioForm(),
        'comentarios': comentarios,
        'guia_resultado': guia_resultado,
     }   
    return render(request, 'home.html', data)
@login_required
def cambiar_contraseña(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            
            update_session_auth_hash(request, user)
            messages.success(request, '¡Contraseña cambiada con éxito!')
            return redirect('index')  

    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/cambiar_contraseña.html', {'form': form})



tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS , IntegrationApiKeys.WEBPAY , IntegrationType.TEST))

def realizar_pago(request, guia_id):
    guia = Guias.objects.get(pk=guia_id)
    crear_transaccion = tx.create(str(guia.id), "123", guia.saldo, "http://127.0.0.1:8000/retorno_webpay/")
    url = crear_transaccion['url']
    token = crear_transaccion['token']
    url_completa = url + "?token_ws=" + token
    #crear_transaccion.url
    #crear_transaccion.token
    return HttpResponseRedirect(url_completa)

def retorno_webpay(request):
    token = request.GET.get("token_ws")
    response = Transaction().commit(token=token)

    # Imprimir la respuesta completa para inspeccionar su estructura
    print("Transbank Response:", response, response['response_code'] )

    # Verifica si la transacción fue exitosa antes de cambiar el estado de la guía
    if response['response_code'] == 0:
        # Encuentra la guía asociada al token (ajusta según tu modelo y relación)
        guia_id = int(response['buy_order'])
        guia = Guias.objects.get(pk=guia_id)
        
        # Cambia el estado de la guía a "completado" u otro estado deseado
        guia.estado_pago = 'completado'
        guia.save()
        messages.success(request, "Pago completado")
    else:
        messages.warning(request, "Pago fallido")
        

    return redirect('home')




    




    

