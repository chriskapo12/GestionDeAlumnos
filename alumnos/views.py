from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .forms import AlumnoForm, SignUpForm
from .models import Alumno
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def home(request):
    """Página principal"""
    if request.user.is_authenticated:
        return redirect('alumnos:dashboard')
    return render(request, 'alumnos/home.html')

def login_view(request):
    """Vista de inicio de sesión"""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('alumnos:dashboard')
        else:
            return render(request, 'alumnos/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'alumnos/login.html')

def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    return redirect('alumnos:login')

def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # enviar correo de bienvenida
            subject = "Bienvenido/a"
            body = render_to_string('emails/bienvenida.html', {'user': user})
            email = EmailMessage(subject, body, to=[user.email])
            email.content_subtype = "html"
            email.send(fail_silently=True)
            login(request, user)
            return redirect('alumnos:dashboard')
    else:
        form = SignUpForm()
    return render(request, 'alumnos/register.html', {'form': form})

@login_required
def dashboard(request):
    form = AlumnoForm()
    if request.method == "POST":
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.user = request.user
            alumno.save()
            return redirect('alumnos:dashboard')
    alumnos = request.user.alumnos.all()
    return render(request, 'alumnos/dashboard.html', {'alumnos': alumnos, 'form': form})

from django.utils import timezone
import time
from django.contrib import messages

@login_required
def enviar_pdf(request, pk):
    # Control de spam: esperar 5 segundos entre envíos
    ultimo_envio = request.session.get('ultimo_envio_pdf')
    ahora = time.time()
    
    if ultimo_envio and (ahora - ultimo_envio) < 5:
        tiempo_restante = int(5 - (ahora - ultimo_envio))
        messages.warning(request, f"Por favor espera {tiempo_restante} segundos antes de enviar otro correo.")
        return redirect('alumnos:dashboard')
    
    # Actualizar tiempo de último envío
    request.session['ultimo_envio_pdf'] = ahora

    alumno = get_object_or_404(Alumno, pk=pk, user=request.user)
    # Generar PDF con ReportLab en memoria
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica", 12)
    p.drawString(50, 800, f"Ficha del alumno: {alumno.nombre}")
    p.drawString(50, 780, f"Curso: {alumno.curso}")
    p.drawString(50, 760, f"Email: {alumno.email}")
    
    # Convertir a hora local antes de mostrar
    fecha_local = timezone.localtime(alumno.creado)
    p.drawString(50, 740, f"Creado: {fecha_local.strftime('%d/%m/%Y %H:%M')}")
    p.showPage()
    p.save()
    buffer.seek(0)

    # Enviar por email al docente o al mismo usuario
    subject = f"Ficha de {alumno.nombre}"
    body = f"Adjunto PDF con datos del alumno {alumno.nombre}."
    email = EmailMessage(subject, body, to=[request.user.email])  # o docente@example.com
    email.attach(f"alumno_{alumno.id}.pdf", buffer.read(), 'application/pdf')
    email.send(fail_silently=False)
    
    messages.success(request, f"PDF de {alumno.nombre} enviado correctamente a tu correo.")
    return redirect('alumnos:dashboard')
