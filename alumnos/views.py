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

import threading

# Función auxiliar para enviar email de bienvenida en segundo plano
def send_welcome_email_thread(user):
    try:
        subject = "Bienvenido/a"
        body = render_to_string('emails/bienvenida.html', {'user': user})
        email = EmailMessage(subject, body, to=[user.email])
        email.content_subtype = "html"
        email.send(fail_silently=True)
    except Exception as e:
        print(f"Error enviando email bienvenida: {e}")

# Función auxiliar para enviar PDF en segundo plano
def send_pdf_email_thread(user_email, alumno_nombre, pdf_content):
    try:
        subject = f"Ficha de {alumno_nombre}"
        body = f"Adjunto PDF con datos del alumno {alumno_nombre}."
        email = EmailMessage(subject, body, to=[user_email])
        email.attach(f"alumno.pdf", pdf_content, 'application/pdf')
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Error enviando PDF: {e}")

def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Enviar correo en un hilo separado para no bloquear/romper el server
            email_thread = threading.Thread(target=send_welcome_email_thread, args=(user,))
            email_thread.start()
            
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
    
    # Obtener el contenido del PDF para enviarlo
    pdf_content = buffer.getvalue()
    buffer.close()

    # Enviar por email en segundo plano (threading)
    email_thread = threading.Thread(
        target=send_pdf_email_thread, 
        args=(request.user.email, alumno.nombre, pdf_content)
    )
    email_thread.start()
    

from django.http import HttpResponse

@login_required
def test_email(request):
    """Vista para probar la configuración de correo y ver errores en pantalla"""
    try:
        subject = "Prueba de Diagnóstico - Render"
        body = "Si lees esto, el email funciona correctamente desde Render."
        email = EmailMessage(subject, body, to=[request.user.email])
        
        # Intentamos enviar (sin fail_silently para ver el error)
        email.send(fail_silently=False)
        
        return HttpResponse(f"""
            <div style='font-family: sans-serif; padding: 20px; background: #d4edda; color: #155724; border: 1px solid #c3e6cb; border-radius: 5px;'>
                <h1>✅ ÉXITO</h1>
                <p>El correo se envió correctamente a: <strong>{request.user.email}</strong></p>
                <p>Revisa tu bandeja de entrada (y spam).</p>
                <a href='/dashboard/'>Volver al Dashboard</a>
            </div>
        """)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return HttpResponse(f"""
            <div style='font-family: monospace; padding: 20px; background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 5px;'>
                <h1>❌ ERROR DE ENVÍO</h1>
                <p>Ocurrió un error al intentar enviar el correo:</p>
                <pre style='background: #fff; padding: 15px; border: 1px solid #ddd; overflow-x: auto;'>{error_details}</pre>
                <p><strong>Sugerencias:</strong></p>
                <ul>
                    <li>Verifica que EMAIL_USER y EMAIL_PASSWORD sean correctos en Render.</li>
                    <li>Asegúrate de que la contraseña no tenga espacios.</li>
                    <li>Verifica que la "Verificación en 2 pasos" siga activa en Google.</li>
                </ul>
                <a href='/dashboard/'>Volver al Dashboard</a>
            </div>
        """)
