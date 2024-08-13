from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from users.form import  UserLoginForm, UserRegistrationForm, ProfileForm


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)

                if request.POST.get('next', None):
                    return HttpResponseRedirect(request.POST.get('next'))


                return render(request, 'app/index.html')
                # return HttpResponseRedirect(reverse('app:index'))
            
    else:
        form = UserLoginForm()

        
    context = {
        "form": form
    }

    return render(request, 'users/login.html', context=context)

def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            auth.login(request, user)
            return HttpResponseRedirect(reverse('users:login'))
    else:
        form = UserRegistrationForm()

    context = {
        'form': form
    }

    return render(request, 'users/registration.html', context=context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():

            form.save()

            return HttpResponseRedirect(reverse('users:profile'))
        
        
    else:
        form = ProfileForm(instance=request.user)

    context = {
        'form': form
    }

    return render(request, 'users/profile.html', context=context)

@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse("app:index"))