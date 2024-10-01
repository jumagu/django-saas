from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

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

# def register_view(request):
#     return render(request, 'auth/register.html', {})
