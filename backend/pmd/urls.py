
from django.contrib import admin
from django.urls import path, include
from trackapi.metrics import metrics_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        '',include('prontuarios.urls')
    ),
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'api/token/verify/',
        TokenVerifyView.as_view(),
        name='token_verify'
    ),
    path(
        'eventos/',
        include('trackapi.urls')
    ),
    path(
        'metrics',
        metrics_view,
        name='metrics'
    ),
]
