import streamlit as st
from utils.api_client import APIClient
import json
import pandas as pd
from datetime import datetime
from utils.auth import check_admin_access, add_logout_sidebar

api_client = APIClient()

st.set_page_config(
    layout="wide", 
    page_title="Pagamentos",
    initial_sidebar_state="collapsed"
)


def mock_payment_process(service_id, payment_method, amount):
    """Mock payment process for testing without the backend endpoint"""
    return {
        "status": "success",
        "message": "Pagamento processado com sucesso (modo simulação)",
        "payment_id": 999,
        "amount": amount,
        "method": payment_method
    }, True


def process_payment(service_id, payment_method, amount):
    """Process a payment through the API"""
    payload = {
        "servico_id": service_id,
        "payment_method": payment_method,
        "amount": amount
    }
    
    st.session_state.debug_info = {
        "payload": payload,
        "endpoint": "/api/process-payment/"
    }
    
    try:

        response = api_client.post("/api/process-payment/", json=payload)
        

        st.session_state.debug_info["status_code"] = response.status_code
        st.session_state.debug_info["response_text"] = response.text
        
        if response.status_code == 200:
            return response.json(), True
        else:
            error_msg = "Erro desconhecido"
            try:
                error_data = response.json()
                error_msg = error_data.get("error", error_msg)
            except Exception as e:
        
                error_msg = f"Erro no formato da resposta: {str(e)}. Resposta: {response.text[:100]}"
            
            return {"error": error_msg}, False
            
    except Exception as e:

        error_detail = str(e)
        st.session_state.debug_info["exception"] = error_detail
        return {"error": f"Erro de conexão: {error_detail}"}, False


def payment_form(service):
    """Display payment form for a service"""
    st.subheader(f"Processar Pagamento para Serviço #{service['servico_ID']}")
    
    st.write(f"Cliente: {service.get('cliente_nome', 'N/A')}")
    st.write(f"Valor do Orçamento: R$ {service.get('orcamento', 0):.2f}")
    
    with st.form("payment_form"):
        payment_method = st.selectbox(
            "Método de Pagamento",
            options=["cash", "credit_card", "debit_card", "bank_transfer", "pix"],
            format_func=lambda x: {
                "cash": "Dinheiro",
                "credit_card": "Cartão de Crédito",
                "debit_card": "Cartão de Débito",
                "bank_transfer": "Transferência Bancária",
                "pix": "PIX"
            }.get(x, x)
        )
        

        raw_amount = service.get('orcamento', 0)
        default_amount = max(0.01, float(raw_amount))
        

        if 0 < raw_amount < 0.01:
            st.warning(f"O valor original (R$ {raw_amount:.6f}) foi arredondado para o mínimo de R$ 0.01")
        
        amount = st.number_input(
            "Valor do Pagamento", 
            min_value=0.01, 
            value=default_amount,
            format="%.2f"
        )
        

        if payment_method == "credit_card":
            st.text_input("Número do Cartão (Simulado)", value="4111111111111111")
            st.text_input("Nome no Cartão", value="USUARIO TESTE")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Validade", value="12/25")
            with col2:
                st.text_input("CVV", value="123", type="password")
                
        elif payment_method == "pix":
            st.info("Um QR Code seria gerado aqui em um sistema real")
            st.code("PIXKEY123456789", language=None)
        
        submitted = st.form_submit_button("Processar Pagamento")
    
    if submitted:

        result, success = mock_payment_process(service['servico_ID'], payment_method, amount)
        
        if success:
            st.success(f"Pagamento processado com sucesso! Método: {payment_method.upper()}")
            
    
            if result.get("status") == "success":
        
                try:
                    status_response = api_client.post(
                        f"/api/status/",
                        json={
                            "servico_ID": service['servico_ID'],
                            "status": "Finalizado",
                            "observacao": f"Pagamento de R$ {amount:.2f} recebido via {payment_method}"
                        }
                    )
                    
                    if status_response.status_code in (200, 201):
                        st.success("Status do serviço atualizado para Finalizado!")
                
                        if st.button("↻ Atualizar Lista"):
                            st.rerun()
                    else:
                        st.warning(f"Pagamento processado, mas não foi possível atualizar o status do serviço. Código: {status_response.status_code}")
                except Exception as e:
                    st.warning(f"Pagamento processado, mas ocorreu um erro ao atualizar o status: {str(e)}")
        
        else:
            st.error(f"Erro ao processar pagamento: {result.get('error', 'Erro desconhecido')}")
    
            with st.expander("Detalhes do erro (para desenvolvedores)"):
                st.write("Dados enviados:")
                st.json({
                    "service_id": service['servico_ID'],
                    "payment_method": payment_method,
                    "amount": amount
                })
                if "debug_info" in st.session_state:
                    st.write("Detalhes da requisição:")
                    st.json(st.session_state.debug_info)

def fetch_data():
    """Fetch all necessary data for the payments page"""
    services = api_client.get("/api/servicos/").json() if api_client.get("/api/servicos/").status_code == 200 else []
    
    clients = api_client.get("/api/clientes/").json() if api_client.get("/api/clientes/").status_code == 200 else []
    clients_dict = {c["cliente_ID"]: c for c in clients}
    
    payments = api_client.get("/api/pagamentos/").json() if api_client.get("/api/pagamentos/").status_code == 200 else []
    payments_dict = {p["pagamento_ID"]: p for p in payments}
    
    for service in services:

        client_id = service.get("cliente")
        if client_id in clients_dict:
            service["cliente_nome"] = clients_dict[client_id].get("nome", "Cliente Desconhecido")
        else:
            service["cliente_nome"] = "Cliente Desconhecido"
        

        payment_id = service.get("pagamento")
        if payment_id and payment_id in payments_dict:
            service["payment_status"] = payments_dict[payment_id].get("status", "Pendente")
            service["payment_method"] = payments_dict[payment_id].get("metodo_pagamento", "Não informado")
            service["payment_amount"] = payments_dict[payment_id].get("valor_final", 0)
        else:
            service["payment_status"] = "Pendente"
            service["payment_method"] = "Não informado" 
            service["payment_amount"] = 0
    
    return services, payments

def main():
    """Main function for the payments page"""
    check_admin_access()
    add_logout_sidebar()
    st.title("💰 Gestão de Pagamentos")
    
    services, payments = fetch_data()
    
    tab1, tab2, tab3 = st.tabs(["Pendentes", "Todos os Pagamentos", "Relatórios"])
    

    with tab1:
        st.header("Serviços com Pagamento Pendente")
        

        payment_needed = [s for s in services if 
                         s.get("status_atual") in ["Aprovado", "Em Andamento", "Diagnóstico Adicional", "Finalizado"] 
                         and s.get("payment_status") != "Pago"]
        
        if not payment_needed:
            st.info("Não há serviços pendentes de pagamento.")
        else:
    
            pending_data = []
            for service in payment_needed:
                pending_data.append({
                    "ID": service.get("servico_ID"),
                    "Cliente": service.get("cliente_nome", "N/A"),
                    "Status": service.get("status_atual", "N/A"),
                    "Valor": f"R$ {service.get('orcamento', 0):.2f}",
                    "Entrada": service.get("data_entrada", "N/A")
                })
                
    
            pending_df = pd.DataFrame(pending_data)
            
    
            selected_idx = st.selectbox(
                "Selecione um serviço para pagamento:",
                options=range(len(pending_data)),
                format_func=lambda i: f"#{pending_data[i]['ID']} - {pending_data[i]['Cliente']} - {pending_data[i]['Valor']}"
            )
            
            if st.button("Processar Pagamento", key="process_selected_payment"):
                selected_service_id = pending_data[selected_idx]["ID"]
        
                selected_service = next((s for s in services if s.get("servico_ID") == selected_service_id), None)
                if selected_service:
                    st.session_state.selected_service = selected_service
                    st.session_state.show_payment_form = True
                    st.rerun()
        

        if st.session_state.get('show_payment_form', False) and 'selected_service' in st.session_state:
            payment_form(st.session_state.selected_service)
    
    with tab2:
        st.header("Histórico de Pagamentos")
        

        all_payments_data = []
        for service in services:
    
            if service.get("payment_amount", 0) > 0:
                all_payments_data.append({
                    "ID": service.get("servico_ID"),
                    "Cliente": service.get("cliente_nome", "N/A"),
                    "Valor": f"R$ {service.get('payment_amount', 0):.2f}",
                    "Método": service.get("payment_method", "N/A"),
                    "Status": service.get("payment_status", "Pendente"),
                    "Data": service.get("data_entrada", "N/A") 
                })
        
        if not all_payments_data:
            st.info("Não há histórico de pagamentos registrado.")
        else:
            payments_df = pd.DataFrame(all_payments_data)
            st.dataframe(payments_df, use_container_width=True)
    
    with tab3:
        st.header("Relatórios Financeiros")
        

        total_pending = sum(s.get("orcamento", 0) for s in services if s.get("payment_status") != "Pago")
        total_paid = sum(s.get("payment_amount", 0) for s in services if s.get("payment_status") == "Pago")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Recebido", f"R$ {total_paid:.2f}")
        with col2:
            st.metric("Pendente de Recebimento", f"R$ {total_pending:.2f}")
        with col3:
            if total_paid + total_pending > 0:
                payment_rate = (total_paid / (total_paid + total_pending)) * 100
                st.metric("Taxa de Recebimento", f"{payment_rate:.1f}%")
            else:
                st.metric("Taxa de Recebimento", "N/A")
        

        st.subheader("Distribuição por Método de Pagamento")
        
        payment_methods = {}
        for service in services:
            if service.get("payment_status") == "Pago":
                method = service.get("payment_method", "Não informado")
                payment_methods[method] = payment_methods.get(method, 0) + service.get("payment_amount", 0)
        
        if payment_methods:
            methods_df = pd.DataFrame({
                "Método": list(payment_methods.keys()),
                "Valor": list(payment_methods.values())
            })
            
    
            import plotly.express as px
            fig = px.pie(methods_df, values='Valor', names='Método', title='Distribuição por Método de Pagamento')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados suficientes para gerar o gráfico.")
        

        st.subheader("Receita Mensal")
        

        monthly_revenue = {}
        for service in services:
            if service.get("payment_status") == "Pago":
                try:
                    date_str = service.get("data_entrada", "")
                    if date_str:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                        month_key = f"{date.year}-{date.month:02d}"
                        monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + service.get("payment_amount", 0)
                except:
                    pass
        
        if monthly_revenue:
    
            sorted_months = sorted(monthly_revenue.keys())
            revenue_df = pd.DataFrame({
                "Mês": [f"{m.split('-')[0]}-{m.split('-')[1]}" for m in sorted_months],
                "Receita": [monthly_revenue[m] for m in sorted_months]
            })
            
    
            fig = px.bar(revenue_df, x='Mês', y='Receita', title='Receita Mensal')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados suficientes para gerar o gráfico de receita mensal.")

if __name__ == "__main__":
    if 'show_payment_form' not in st.session_state:
        st.session_state.show_payment_form = False
    
    main()
    
    components_html = """
    <script>
    // Listen for messages from the Streamlit app
    window.addEventListener('message', function(event) {
        // Check if the message is a custom component value
        if (event.data.type === 'streamlit:setComponentValue') {
            // Extract the service ID and add it to the URL parameters
            const serviceId = event.data.value;
            if (serviceId) {
                const url = new URL(window.location.href);
                url.searchParams.set('pay_service', serviceId);
                window.history.pushState({}, '', url);
                window.location.reload();
            }
        }
    });
    </script>
    """
    st.components.v1.html(components_html, height=0)