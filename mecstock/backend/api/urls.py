from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet)
router.register(r'carros', views.CarroViewSet)
router.register(r'pagamentos', views.PagamentoViewSet)
router.register(r'mecanicos', views.MecanicoViewSet)
router.register(r'servicos', views.ServicoViewSet)
router.register(r'enderecos', views.EnderecoViewSet)
router.register(r'insumos', views.InsumoViewSet)
router.register(r'status', views.StatusViewSet)

urlpatterns = [
    path('', include(router.urls)),
]