from django.urls import path

from apps.lector import views

urlpatterns = [
    # API Version 1
    path('open-spaces/<str:file_name>/plot/', views.ApiOpenSpacePlot.as_view(), name='open-space-plot'),
]
