from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login,authenticate
from django.contrib import messages
# Create your views here.

def home_view(request):
    return render(request,'home.html')


def login_handle_view(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        user = authenticate(username = username, password=password)
        if user is not None:
            login(request,user)
            return HttpResponse('hi')
        else:
            messages.error(request,"Invalid username or password.")
            return render(request,'home.html')