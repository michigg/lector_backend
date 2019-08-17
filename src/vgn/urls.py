from django.urls import path

from vgn import views

urlpatterns = [
    # API Version 1
    path('vgn/', views.ApiVGNConnection.as_view(), name='vgn-connection'),
]
