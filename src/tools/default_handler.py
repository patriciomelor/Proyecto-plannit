from django.shortcuts import render
from django.http import HttpResponse

def error_400_view(request, exception):
    data = {}
    return render(request, 'tools/400.html', data)

def error_403_view(request, exception):
    data = {}
    return render(request, 'tools/403.html', data)

def error_404_view(request, exception):
    data = {}
    return render(request, 'tools/404.html', data)

def error_500_view(request):
    data = {}
    return render(request, 'tools/500.html', data)
    
    