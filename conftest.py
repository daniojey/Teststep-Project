import pytest
from main import settings

def pytest_configure():
    settings.STORAGES['staticfiles']['BACKEND'] = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    settings.STORAGES['default']['BACKEND'] = (
        "django.core.files.storage.FileSystemStorage"
    )

    if "whitenoise" in settings.INSTALLED_APPS:
        from whitenoise.storage import CompressedManifestStaticFilesStorage
        settings.STORAGES["staticfiles"]["BACKEND"] = CompressedManifestStaticFilesStorage