from django.urls import path

from . import views

urlpatterns = [
    # API Version 1
    path('movement-types/', views.ApiListMovementTypes.as_view(), name='movement-types'),
    path('open-spaces/', views.ApiListOpenSpaces.as_view(), name='open-spaces'),
    path('open-spaces/<str:file_name>/geojson/', views.ApiListOpenSpaceGeoJson.as_view(), name='open-space'),
    path('open-spaces/<str:file_name>/config/', views.ApiListOpenSpaceConfig.as_view(), name='open-space'),
    # path('open-spaces/<str:file_name>/plot/', views.ApiOpenSpacePlot.as_view(), name='open-space-plot'),
]
