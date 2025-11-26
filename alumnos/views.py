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
import threading


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


# -----------------------------
#  ENVÍO EMAIL DE BIENVENIDA
# -----------------------------
def send_welcome_email_thread(user):
    try:
        subject = "Bienvenido/a"
        body = render_to_string('emails/bienvenida.html', {'user': user})
        email = EmailMessage(subject, body, to=[user.email])
        email.content_subtype = "html"
        email.send(fail_silently=True)
    except Exception as e:
        print(f"Error enviando email bienvenida: {e}")


def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            email_thread = threading.Thread(target=send_welcome_email_thread, args=(user,))
            email_thread.start()

            login(request, user)
            return redirect('alumnos:dashboard')
    else:
        form = SignUpForm()
    return render(request, 'alumnos/register.html', {'form': form})


# -----------------------------
#  DASHBOARD
# -----------------------------
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


# -----------------------------
#  ENVÍO PDF
# -----------------------------
from django.utils import timezone
import time
from django.contrib import messages


def send_pdf_email_thread(user_email, alumno_nombre, pdf_content):
    try:
        subject = f"Ficha de {alumno_nombre}"
        body = f"Adjunto PDF con datos del alumno {alumno_nombre}."
        email = EmailMessage(subject, body, to=[user_email])
        email.attach("alumno.pdf", pdf_content, 'application/pdf')
        email.send(fail_silently=True)
    except Exception as e:
        print("Error enviando PDF:", e)


@login_required
def enviar_pdf(request, pk):

    ultimo_envio = request.session.get('ultimo_envio_pdf')
    ahora = time.time()

    if ultimo_envio and (ahora - ultimo_envio) < 5:
        tiempo_restante = int(5 - (ahora - ultimo_envio))
        messages.warning(request, f"Por favor espera {tiempo_restante} segundos antes de enviar otro correo.")
        return redirect('alumnos:dashboard')

    request.session['ultimo_envio_pdf'] = ahora

    alumno = get_object_or_404(Alumno, pk=pk, user=request.user)

    # Generar PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica", 12)
    p.drawString(50, 800, f"Ficha del alumno: {alumno.nombre}")
    p.drawString(50, 780, f"Curso: {alumno.curso}")
    p.drawString(50, 760, f"Email: {alumno.email}")

    fecha_local = timezone.localtime(alumno.creado)
    p.drawString(50, 740, f"Creado: {fecha_local.strftime('%d/%m/%Y %H:%M')}")

    p.showPage()
    p.save()

    pdf_content = buffer.getvalue()
    buffer.close()

    # Enviar en hilo
    thread = threading.Thread(target=send_pdf_email_thread,
                              args=(request.user.email, alumno.nombre, pdf_content))
    thread.start()

    messages.success(request, f"PDF de {alumno.nombre} se está enviando a tu correo.")
    return redirect('alumnos:dashboard')


# -----------------------------
#  TEST CORREO
# -----------------------------
from django.http import HttpResponse


@login_required
def test_email(request):
    try:
        email = EmailMessage("Prueba", "Mensaje de prueba desde Render.", to=[request.user.email])
        email.send(fail_silently=False)

        return HttpResponse("<h1>Correo enviado correctamente</h1>")
    except Exception as e:
        return HttpResponse(f"<h1>Error enviando correo:</h1><pre>{e}</pre>")
