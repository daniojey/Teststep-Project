from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from tests.models import TestResult, TestsReviews
from django.http import JsonResponse

from .models import User, UsersGroup, UsersGroupMembership

from users.form import  UserLoginForm, UserRegistrationForm, ProfileForm


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(email=email, password=password)
            if user:
                auth.login(request, user)

                if request.POST.get('next', None):
                    return HttpResponseRedirect(request.POST.get('next'))


                return redirect("app:index")
                # return HttpResponseRedirect(reverse('app:index'))
        else:
                print(form.errors)
            
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
            user = form.save(commit=False)
            
            base_name = f"{form.cleaned_data['first_name'][0]}{form.cleaned_data['last_name']}".lower()
            username = base_name
            count = 1

            while User.objects.filter(username=username).exists():
                username = f"{base_name}_{count}"
                count += 1

            user.username = username
            
            user.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse('app:index'))
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
        'active_tab': 'profile',

    }

    return render(request, 'users/profile.html', context=context)

@login_required
@csrf_exempt  # Для AJAX запросов без формы
def profile_image_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        user_profile = request.user  # Достаем профиль пользователя
        user_profile.image = request.FILES['image']
        user_profile.save()

        # Отправляем обратно URL нового изображения
        return JsonResponse({
            'success': True,
            'image_url': user_profile.image.url
        })

    return JsonResponse({
        'success': False,
        'error': 'Не удалось загрузить изображение'
    })


@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse("app:index"))