from django.urls import path, include
from .swagger import urlpatterns as swagger_urls


urlpatterns = [
    path('api/', include('api.urls')),
]

urlpatterns += swagger_urls