from .strategies.cash import CashPaymentStrategy
from .strategies.credit_card import CreditCardPaymentStrategy
from .strategies.debit_card import DebitCardPaymentStrategy
from .strategies.bank_transfer import BankTransferPaymentStrategy
from .strategies.pix import PixPaymentStrategy
from ..models import Pagamento, Servico

class PaymentService:
    """Service class that uses strategy pattern but works with the Pagamento model"""
    
    def __init__(self):
        self.strategies = {
            'cash': CashPaymentStrategy(),
            'credit_card': CreditCardPaymentStrategy(),
            'debit_card': DebitCardPaymentStrategy(),
            'bank_transfer': BankTransferPaymentStrategy(),
            'pix': PixPaymentStrategy()
        }
    
    def process_payment(self, servico_id, payment_method, amount, **kwargs):
        """Process payment and update the Pagamento model"""
        
        if payment_method not in self.strategies:
            raise ValueError(f"Método de pagamento não suportado: {payment_method}")
        
        try:
            servico = Servico.objects.get(servico_ID=servico_id)
            
            strategy = self.strategies[payment_method]
            payment_result = strategy.process_payment(amount, **kwargs)
            
            if hasattr(servico, 'pagamento') and servico.pagamento:
                pagamento = servico.pagamento
            else:
                pagamento = Pagamento()
                
            pagamento.valor_total = servico.orcamento
            pagamento.valor_final = amount
            pagamento.metodo_pagamento = payment_method
            pagamento.status = 'Pago' if payment_result['status'] == 'success' else 'Pendente'
            pagamento.save()
            
            if not servico.pagamento:
                servico.pagamento = pagamento
                servico.save()
                
            return payment_result, pagamento
            
        except Servico.DoesNotExist:
            raise ValueError(f"Serviço não encontrado: {servico_id}")
        except Exception as e:
            raise Exception(f"Erro ao processar pagamento: {str(e)}")