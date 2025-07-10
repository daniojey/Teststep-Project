from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from tests.models import Tests

class CheckPersonalMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.teacher and not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied('Отказано в доступе')
    
        return super().dispatch(request, *args, **kwargs)

class TestcheckOwnerOrAdminMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied('Зарегестрируйтесь')
        
        test_id = kwargs.get('test_id')
        
        try:
            obj = Tests.objects.select_related('user').get(id=test_id)
        except Tests.DoesNotExist:
            raise Http404('Test not found')

        if not hasattr(obj, 'user'):
            raise AttributeError('Неверный объект')
        
        if obj.user != request.user and not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied('Отказано в доступе')
    
        return super().dispatch(request, *args, **kwargs)