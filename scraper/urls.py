from django.urls import path
from . import views

app_name = "scraper"

urlpatterns = [
    path('buscar/', views.buscar, name='buscar'),
]
