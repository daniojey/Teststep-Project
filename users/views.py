import json
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.db.models import Prefetch
from django.db.models.base import Model as Model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.views.generic import FormView, CreateView, UpdateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from tests.models import Tests
from users.custom_utils.parser_utils import exel_parser, xml_parser
from .utils import is_blocked
from django.db import transaction
from main.settings import ENABLE_DEMO, ENABLE_SMTP

from .models import Group, LoginAttempt, User

from users.form import  UserLoginForm, UserRegistrationForm, ProfileForm


class UserLoginView(FormView):
    template_name = "users/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("app:index")

    def form_valid(self, form):        
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        ip_address = self.request.META.get('REMOTE_ADDR')
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        print(ip_address)
        print(user_agent)

        # Проверяем заблокирован ли пользователь
        if is_blocked(email=email, ip_address=ip_address):
            status = form.add_error(None, 'Ваш обліковий запис тимчасово заблокованый, спробуйте через деякий час')
            print(status)
            return self.form_invalid(form)

        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            self.object = user
            LoginAttempt.objects.create(email=email, ip_address=ip_address, success=True)
            login(self.request, user)

            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"status": "success", "message": f"З поверненням {user.first_name.capitalize()}!"})
            else:
                return super().form_valid(form)

            # Если есть параметр next в post запросе
            next_url = self.request.POST.get('next', None)
            if next_url:
                return redirect(next_url)
            
            return redirect(self.get_success_url())
        else:
           # Неудачная попытка входа
            LoginAttempt.objects.create(email=email, ip_address=ip_address,  success=False)
            form.add_error(None, 'Невірний логін або пароль')
            print()
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        # Получаем данные из запроса
        email = self.request.POST.get('email', '')
        ip_address = self.request.META.get('REMOTE_ADDR')
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        # Проверяем, заблокирован ли пользователь
        if is_blocked(email=email, ip_address=ip_address):
            return JsonResponse({"status": "error", "message": "Ваш обліковий запис тимчасово заблокованый, спробуйте через деякий час"})

        # Логируем неудачную попытку из-за невалидной формы
        status = LoginAttempt.objects.create(email=email, ip_address=ip_address, success=False)
        print(status)

        # Возвращаем ошибку
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            error_message = next(iter(form.errors.values()))[0] if form.errors else "Невідома помилка"
            return JsonResponse({"status": "error", "message": error_message})
        
        return super().form_invalid(form)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['smtp_work'] = True if ENABLE_SMTP == 'True' else False
        context['demo_work'] = True if ENABLE_DEMO == 'True' else False
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

        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            form.add_error('email', 'Этот email уже зарегистрирован. Пожалуйста, используйте другой.')
            return self.form_invalid(form)

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

class CreateDemoUser(View):
    template_name = "users/login.html"
    # success_url = reverse_lazy("app:index")

    def post(self, request, *args, **kwargs):
        # Проверяем наличие блокировки
        ip_address = self.request.META.get('REMOTE_ADDR')
        if is_blocked(ip_address=ip_address, timeframe=800, limit=2):
            return JsonResponse({'status': 'error'}, status= 400)
        
        username = self.generate_uuid_from_user()

        # Проверяем уникальность username
        while True:
            if User.objects.filter(username=username).exists():
                username = self.generate_uuid_from_user()
            else:
                break
        
        password = str(uuid.uuid4()).replace('-', '')[:10]

        try:
            created_user = User.objects.create_user(
                first_name='demo',
                last_name='user',
                username=username,
                password=password,
                is_demo=True
            )

            # LoginAttempt.objects.create(ip_address=ip_address, success=False)

            login(request, created_user)

        except Exception as e:
            return JsonResponse({'status': 'error'}, status= 400)

        try:
            group = Group.objects.prefetch_related(
                Prefetch(
                    "test_group",
                    queryset=Tests.objects.all(),
                    to_attr="all_tests"
                )
            ).get(name="Demo-Group")
        except Group.DoesNotExist:
            group = Group.objects.prefetch_related(
                Prefetch(
                    "test_group",
                    queryset=Tests.objects.all(),
                    to_attr="all_tests"
                )
            ).first()

        group.members.add(created_user)

        # pprint.pprint(group.all_tests)
        if group.all_tests:
            test_ids = [test.id for test in group.all_tests]

            through_model  = Tests.students.through
            with transaction.atomic():
                through_model.objects.bulk_create([
                    through_model(
                        tests_id=test_id,
                        user_id=created_user.id,
                    ) for test_id in test_ids
                ])

        
        return JsonResponse({'status': 'success', 'message': 'Your welcome!'}, status=201)


    def generate_uuid_from_user(*args, **kwargs):
        """ Создание username с уникальным uuid"""

        short_uuid = str(uuid.uuid4()).replace('-', '')[:7]
        return f'user{short_uuid}'
    

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "active_tab":"profile",
        })

        return context
    
    def form_valid(self, form):
        # Сохраняем данные формы
        form.save()
        return super().form_valid(form)

# @login_required
# def profile(request):
#     test_results = request.user.test_results.all().order_by('-date_taken')
#     user = get_object_or_404(User, id=request.user.id)
#     tests_reviews = TestsReviews.objects.filter(user=user).order_by('date_taken')

#     user_groups = UsersGroupMembership.objects.filter(user=user)

    # if user_groups.exists():
    #     group = user_groups.first().group
    #     group_memberships = UsersGroupMembership.objects.filter(group=group)
    #     group_name = group.name
    # else:
    #     group = None
    #     group_memberships = None
    #     group_name = "Вы не присоединились к группе"


#     if request.method == 'POST':
#         form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
#         if form.is_valid():

#             form.save()

#             return HttpResponseRedirect(reverse('users:profile'))
        
        
#     else:
#         form = ProfileForm(instance=request.user)

#     context = {
#         'form': form,
#         'test_results': test_results,
#         'user_group': group,
#         'group_name': group_name,
#         'group_memberships': group_memberships,
#         'user_test_reviews': tests_reviews,
#         'active_tab': 'profile',

#     }

#     return render(request, 'users/profile.html', context=context)

login_required
def profile_image_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            user_profile = request.user
            user_profile.image = request.FILES['image']
            user_profile.save()

            return JsonResponse({
                'success': True,
                'image_url': user_profile.image.url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'error': 'Не удалось загрузить изображение'
    }, status=400)


@login_required
def logout(request):
    user = request.user

    auth.logout(request)

    if user.is_demo:
        # print('demoUSER')
        user.delete()
        print('DEMO USER HAS BEEN DELETE')
        
    return redirect(reverse("users:login"))


class AddUsersView(View):
    def post(self, request, *args, **kwargs):
        action = request.META.get('X-Action') or request.POST.get('action')

        if action == 'getUsers':
            file = request.FILES.get('file')
            
            if not file:
                return JsonResponse({'error': 'Файл не прикріплений'}, status=400)
            
            file_extension = file.name.split('.')[-1].lower()

            if file_extension == 'xml':
                result, data  = xml_parser(file=file)
                if result == "success":
                    users= data
                else:
                    return JsonResponse({'error': 'Помилка обробки документу', 'detail': f"{data}"}, status=400)
                
            elif file_extension == 'xls':
                result, data = exel_parser(file=file, format_file="xls")
                if result == 'success':
                    users = data
                else:
                    return JsonResponse({'error': 'Помилка обробки документу', 'detail': f"{data}"}, status=400)
                
            elif file_extension == "xlsx":
                result, data = exel_parser(file=file, format_file="xlsx")
                if result == 'success':
                    users = data
                else:
                    return JsonResponse({'error': 'Помилка обробки документу', 'detail': f"{data}"}, status=400)

            else:
                return JsonResponse({'error': 'Тип документу не підтримуется для обробки'}, status=400)
            

            return JsonResponse(data={'users': users if users else []},status=200)
        
        elif action == 'createUsers':
            users = request.POST.get('users')
            users_to_create = []
            data = json.loads(users)
            valid_users = [user for user in data if user['overal_valid'] == True]

            try:
                for user in valid_users:
                    first_name = user['first_name']['value']
                    last_name = user['last_name']['value']
                    email = user['email']['value']
                    username = user['username']['value']
                    password = user['password']['value']
                    print('PASSWORD', password)

                    u = User(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email
                    )

                    u.set_password(password)
                    users_to_create.append(u)
                    
                with transaction.atomic():
                    User.objects.bulk_create(users_to_create)

            except Exception as e:
                return JsonResponse(data={'error': 'Помилка при обробці', 'detail': f"{e}"}, status=400)

            return JsonResponse(data={'result': len(users_to_create)}, status=201)
        
