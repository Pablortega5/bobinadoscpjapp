from django import forms
from .models import Guias, Sucursal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Cliente, Comentario
from django.core.validators import MinValueValidator, MaxValueValidator


class GuiaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["saldo"].widget.attrs["readonly"] = True
        self.fields["total"].widget.attrs["readonly"] = True
        self.fields["nombre"].widget.attrs["readonly"] = True
        self.fields["direccion"].widget.attrs["readonly"] = True
        self.fields["correo"].widget.attrs["readonly"] = True
        self.fields["telefono"].widget.attrs["readonly"] = True

    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    estado_pago = forms.ChoiceField(
        label='Estado de Pago',
        choices=Guias._meta.get_field('estado_pago').choices,
        initial='Pendiente',
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    estado = forms.ChoiceField(
        label='Estado',
        choices=Guias._meta.get_field('estado').choices,
        initial='En Proceso',
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Guias
        fields = [
            "nombre",
            "direccion",
            "correo",
            "telefono",
            "sucursal",
            "presupuesto",
            "valor_presupuesto",
            "abono",
            "saldo",
            "total",
            "estado",
            "sucursal",
            "estado_pago",
            "archivo_pdf",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "id": "id_nombre"}
            ),
            "direccion": forms.TextInput(
                attrs={"class": "form-control", "id": "id_direccion"}
            ),
            "correo": forms.TextInput(
                attrs={"class": "form-control", "id": "id_correo"}
            ),
            "telefono": forms.TextInput(
                attrs={"class": "form-control", "id": "id_telefono"}
            ),
            "presupuesto": forms.Textarea(attrs={"class": "form-control"}),
            "valor_presupuesto": forms.NumberInput(attrs={"class": "form-control"}),
            "abono": forms.NumberInput(attrs={"class": "form-control"}),
            "saldo": forms.NumberInput(attrs={"class": "form-control"}),
            "total": forms.NumberInput(attrs={"class": "form-control"}),
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "rut", "direccion", "telefono", "correo"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "rut": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "correo": forms.TextInput(attrs={"class": "form-control"}),
        }


class ComentarioForm(forms.ModelForm):
    calificacion = forms.IntegerField(
        validators=[
            MinValueValidator(1, message="La calificación debe ser al menos 1."),
            MaxValueValidator(10, message="La calificación no puede ser más de 10."),
        ],
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 10}),
    )

    class Meta:
        model = Comentario
        fields = ["autor", "contenido", "calificacion"]

        widgets = {
            "autor": forms.TextInput(attrs={"class": "form-control"}),
            "contenido": forms.Textarea(attrs={"class": "form-control"}),
        }
