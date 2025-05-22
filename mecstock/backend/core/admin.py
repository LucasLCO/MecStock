from django.contrib import admin
from .models.carro import Carro
from .models.cliente import Cliente
from .models.endereco import Endereco
from .models.insumo import Insumo
from .models.mecanico import Mecanico
from .models.pagamento import Pagamento
from .models.servico import Servico
from .models.status import Status

admin.site.register(Carro)
admin.site.register(Cliente)
admin.site.register(Endereco)
admin.site.register(Insumo)
admin.site.register(Mecanico)
admin.site.register(Pagamento)
admin.site.register(Servico)
admin.site.register(Status)