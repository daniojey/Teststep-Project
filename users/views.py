from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.forms import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from tests.models import TestResult, TestsReviews
from django.http import JsonResponse
from django.views.generic import FormView, CreateView
from django.contrib.auth import authenticate, login

from .models import User, UsersGroup, UsersGroupMembership

from users.form import  UserLoginForm, UserRegistrationForm, ProfileForm


class UserLoginView(FormView):
    template_name = "users/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("app:index")

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, email=email, password=password)

        if user is not None:
            self.object = user
            login(self.request, user)

            # Если есть параметр next в post запросе
            next_url = self.request.POST.get('next', None)
            if next_url:
                return redirect(next_url)
            
            return redirect(self.get_success_url())
        else:
            form.add_error(None, 'Невірний логін або пароль')
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        response = super().form_invalid(form)
        
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "LOGIN"
        return context

# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             email = request.POST['email']
#             password = request.POST['password']
#             user = auth.authenticate(email=email, password=password)
#             if user:
#                 auth.login(request, user)

#                 if request.POST.get('next', None):
#                     return HttpResponseRedirect(request.POST.get('next'))


#                 return redirect("app:index")
#         else:
#                 print(form.errors)
            
#     else:
#         form = UserLoginForm()

        
#     context = {
#         "form": form
#     }

#     return render(request, 'users/login.html', context=context)
    
class UserRegistrationView(CreateView):
    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy('app:index')

    def form_valid(self, form):
        user = form.save(commit=False)  # Сохраняем форму без коммита, чтобы задать username вручную

        # Генерация уникального имени пользователя
        base_name = f"{form.cleaned_data['first_name'][0]}{form.cleaned_data['last_name']}".lower()
        username = base_name
        count = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_name}_{count}"
            count += 1

        user.username = username
        user.save()  # Сохраняем пользователя с новым именем

        self.object = user
        auth.login(self.request, user)  # Автоматическая авторизация пользователя после регистрации

        return redirect(self.get_success_url())  # Перенаправляем на главную страницу

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# def registration(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(data=request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
            
#             base_name = f"{form.cleaned_data['first_name'][0]}{form.cleaned_data['last_name']}".lower()
#             username = base_name
#             count = 1

#             while User.objects.filter(username=username).exists():
#                 username = f"{base_name}_{count}"
#                 count += 1

#             user.username = username
            
#             user.save()
#             auth.login(request, user)
#             return HttpResponseRedirect(reverse('app:index'))
#     else:
#         form = UserRegistrationForm()

#     context = {
#         'form': form
#     }

#     return render(request, 'users/registration.html', context=context)

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