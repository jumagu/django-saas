from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

# ! Not recommended - Can't customize
# from django.contrib.auth.models import User

from django.contrib.auth import get_user_model

User = get_user_model()

def login_view(request):
    # This is just for learn purpose
    # There are built-in mechanism validate request data in Django
    if request.method == "POST":
        username = request.POST.get("username") or None
        password = request.POST.get("password") or None
        
        if all([username, password]):
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print("success login")
                return redirect("/")
        
    return render(request, 'auth/login.html', {})

def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email") or None
        username = request.POST.get("username") or None
        password = request.POST.get("password") or None
        
        if all([email, username, password]):
            # Django forms performs this easily
            # email_exist = User.objects.filter(email__iexact=email).exists()
            # username_exist = User.objects.filter(username__iexact=username).exists()
            
            try:
                User.objects.create_user(username=username, email=email, password=password)
            except:
                pass
            
        
    return render(request, 'auth/register.html', {})
