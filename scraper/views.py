from django.shortcuts import render, redirect
from .forms import SearchForm
import requests
from bs4 import BeautifulSoup
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def buscar(request):
    resultados = []
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data['q']
            # ejemplo: scrap simple de wikipedia search results (solo demostración)
            url = f"https://es.wikipedia.org/w/index.php?search={q}"
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.select('.mw-search-result-heading')[:10]:
                a = item.find('a')
                resultados.append({'titulo': a.text.strip(), 'link': 'https://es.wikipedia.org' + a['href']})
            # opcional: enviar por correo
            if request.user.is_authenticated:
                body = render_to_string('scraper/email_resultados.html', {'resultados': resultados, 'query': q})
                email = EmailMessage(f"Resultados de scraping: {q}", body, to=[request.user.email])
                email.content_subtype = "html"
                email.send(fail_silently=True)
    else:
        form = SearchForm()
    return render(request, 'scraper/buscar.html', {'form': form, 'resultados': resultados})
