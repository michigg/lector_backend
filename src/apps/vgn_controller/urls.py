from django.urls import path

from . import views

urlpatterns = [
    # API Version 1
    path('vgn/', views.ApiVGNConnection.as_view(), name='vgn-connection'),
]
