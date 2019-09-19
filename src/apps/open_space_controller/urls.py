from django.urls import path

from . import views

urlpatterns = [
    # API Version 1
    path('open-spaces/', views.ApiListOpenSpaces.as_view(), name='open-spaces'),
    path('open-spaces/<str:file_name>/geojson/', views.ApiListOpenSpaceGeoJson.as_view(), name='open-space-geojson-config'),
    path('open-spaces/<str:file_name>/config/', views.ApiListOpenSpaceConfig.as_view(), name='open-space-config'),
]
