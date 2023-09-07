from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect

from userauths.forms import UserRegisterForm
from userauths.models import Profile, User
# Create your views here.

# RegisterView
def RegisterView(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey {request.user.username}, you are already logged in")
        return redirect('core:feed')   

    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        full_name = form.cleaned_data.get('full_name')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')

        user = authenticate(email=email, password=password)
        login(request, user)

        messages.success(request, f"Hi {request.user.username}, your account have been created successfully.")

        profile = Profile.objects.get(user=request.user)
        profile.full_name = full_name
        profile.phone = phone
        profile.save()

        return redirect('core:feed')
    
    context = {'form':form}
    return render(request, 'userauths/sign-up.html', context)
    

# LoginView
def LoginView(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey {request.user.username}, you are already logged in")
        return redirect('core:feed')
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.warning(request, "you are already logged in")
            else:
                messages.warning(request, "Username or password does not exist")
                return redirect("userauths:sign-up") 
        except:
            messages.error(request, "User does not exist")
    return HttpResponseRedirect("/")

# LogoutVirw
def LogoutView(request):
    logout(request)
    messages.warning(request, "you are logged out")
    return redirect("userauths:sign-up")