
from django.urls import path
from . import views 

urlpatterns = [
    path('prontuario/', views.buscarProntuario),

]
