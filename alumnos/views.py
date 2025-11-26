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
from django.utils import timezone
from django.contrib import messages
import time


# ===========================
#  HOME
# ===========================
def home(request):
    if request.user.is_authenticated:
        return redirect('alumnos:dashboard')
    return render(request, 'alumnos/home.html')


# ===========================
#  LOGIN
# ===========================
def login_view(request):
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


# ===========================
#  LOGOUT
# ===========================
def logout_view(request):
    logout(request)
    return redirect('alumnos:login')


# ===========================
#  EMAILS SIN THREADS (Render los bloquea)
# ===========================
def send_welcome_email(user):
    try:
        subject = "Bienvenido/a"
        body = render_to_string('emails/bienvenida.html', {'user': user})
        email = EmailMessage(subject, body, to=[user.email])
        email.content_subtype = "html"
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Error enviando email bienvenida: {e}")


def send_pdf_email(user_email, alumno_nombre, pdf_content):
    try:
        subject = f"Ficha de {alumno_nombre}"
        body = f"Adjunto PDF con datos del alumno {alumno_nombre}."
        email = EmailMessage(subject, body, to=[user_email])
        email.attach("alumno.pdf", pdf_content, "application/pdf")
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Error enviando PDF: {e}")


# ===========================
#  REGISTER
# ===========================
def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Enviar email directo (sin threads)
            send_welcome_email(user)

            login(request, user)
            return redirect('alumnos:dashboard')
    else:
        form = SignUpForm()

    return render(request, 'alumnos/register.html', {'form': form})


# ===========================
#  DASHBOARD
# ===========================
@login_required
def dashboard(request):
    form = AlumnoForm()

    if request.method == "POST":
        form = AlumnoForm(request.POST)

        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.user = request.user
            alumno.save()
            messages.success(request, "Alumno agregado correctamente.")
            return redirect('alumnos:dashboard')

    alumnos = request.user.alumnos.all()
    return render(request, 'alumnos/dashboard.html', {'alumnos': alumnos, 'form': form})


# ===========================
#  ENVIAR PDF
# ===========================
@login_required
def enviar_pdf(request, pk):

    # Anti-spam 5 segundos
    ultimo_envio = request.session.get('ultimo_envio_pdf')
    ahora = time.time()

    if ultimo_envio and (ahora - ultimo_envio) < 5:
        tiempo_restante = int(5 - (ahora - ultimo_envio))
        messages.warning(request, f"Esperá {tiempo_restante}s antes de enviar otro correo.")
        return redirect('alumnos:dashboard')

    request.session['ultimo_envio_pdf'] = ahora

    alumno = get_object_or_404(Alumno, pk=pk, user=request.user)

    # Crear PDF
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

    # Enviar email directo (sin threads)
    send_pdf_email(request.user.email, alumno.nombre, pdf_content)

    messages.success(request, f"PDF enviado a {request.user.email}. Revisá tu bandeja de entrada.")
    return redirect('alumnos:dashboard')


# ===========================
#  TEST EMAIL (DEBUG)
# ===========================
from django.http import HttpResponse

@login_required
def test_email(request):
    try:
        email = EmailMessage(
            "Prueba de Diagnóstico - Render",
            "Si lees esto, el email funciona bien.",
            to=[request.user.email]
        )
        email.send(fail_silently=False)

        return HttpResponse(f"<h1 style='color:green'>ÉXITO ✔</h1>Se envió a {request.user.email}")
    except Exception as e:
        return HttpResponse(f"<h1 style='color:red'>ERROR ❌</h1><pre>{e}</pre>")
