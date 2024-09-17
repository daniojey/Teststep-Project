from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from tests.models import TestResult, TestsReviews

from .models import User, UsersGroup, UsersGroupMembership

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


                return redirect("users:profile")
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
    test_results = request.user.test_results.all().order_by('-date_taken')
    user = get_object_or_404(User, id=request.user.id)
    tests_reviews = TestsReviews.objects.filter(user=user).order_by('date_taken')

    user_groups = UsersGroupMembership.objects.filter(user=user)

    if user_groups.exists():
        group = user_groups.first().group
        group_memberships = UsersGroupMembership.objects.filter(group=group)
        group_name = group.name
    else:
        group = None
        group_memberships = None
        group_name = "Вы не присоединились к группе"


    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():

            form.save()

            return HttpResponseRedirect(reverse('users:profile'))
        
        
    else:
        form = ProfileForm(instance=request.user)

    context = {
        'form': form,
        'test_results': test_results,
        'user_group': group,
        'group_name': group_name,
        'group_memberships': group_memberships,
        'user_test_reviews': tests_reviews,

    }

    return render(request, 'users/profile.html', context=context)

@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse("app:index"))