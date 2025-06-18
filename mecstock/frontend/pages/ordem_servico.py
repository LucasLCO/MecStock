import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.api_client import APIClient
import plotly.express as px
import time
import altair as alt
from streamlit_extras.card import card
from streamlit_extras.metric_cards import style_metric_cards
import requests
from utils.auth import check_admin_access, add_logout_sidebar

api_client = APIClient()

STATUS_MAPPING = {
    "Cadastrado": "📝",
    "Aguardando Aprovação": "⏳",
    "Aprovado": "✅",
    "Em Andamento": "🔧",
    "Diagnóstico Adicional": "🔍",
    "Aguardando Peças": "🚚",
    "Finalizado": "🏁",
    "Entregue": "🤝",
    "Cancelado": "❌"
}

# Add some custom CSS for better spacing and styling
st.markdown("""
<style>
    .kanban-column {
        background-color: transparent;
        border-radius: 8px;
        padding: 8px;
        margin: 4px;
    }
    .kanban-header {
        text-align: center;
        padding: 10px;
        font-weight: bold;
        border-radius: 6px;
        margin-bottom: 12px;
        background-color: transparent;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
    }
    .service-card {
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 10px;
        transition: transform 0.2s;
        background-color: transparent;
    }
    .service-card:hover {
        transform: translateY(-3px);
    }
    .client-name {
        font-weight: bold;
        font-size: 16px;
    }
    .service-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .service-id {
        font-size: 12px;
        opacity: 0.7;
    }
    .car-info {
        font-size: 14px;
        margin: 5px 0;
    }
    .service-meta {
        display: flex;
        justify-content: space-between;
        margin-top: 8px;
        font-size: 12px;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        border-radius: 12px;
        padding: 3px 8px;
        font-size: 14px;
        background-color: transparent;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .date-badge {
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }
    .dashboard-metric {
        text-align: center;
        padding: 15px;
        border-radius: 8px;
        background-color: transparent;
    }
    .tab-content {
        padding: 20px 0;
    }
    .search-container {
        margin: 15px 0;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.fixed-content) {
        position: sticky;
        top: 2.875rem;
        z-index: 999;
        background-color: transparent;
        padding: 10px 0;
    }
    .detail-header {
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
    }
    
    /* Add these rules to make metric cards transparent */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        background-color: transparent !important;
        color: inherit !important;
    }
    
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricLabel"] > div,
    div[data-testid="stMetricDelta"] > div {
        background-color: transparent !important;
    }
    
    div[data-testid="stMetricValue"] svg,
    div[data-testid="stMetricDelta"] svg {
        background-color: transparent !important;
    }
    
    div[data-testid="metric-container"] {
        background-color: transparent !important;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 5px;
        padding: 10px;
        box-shadow: none !important;
    }
    
    /* Additional fixes for dark mode */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: inherit !important;
    }
    
    /* Fix for dataframes and other white elements */
    [data-testid="stDataFrame"] div {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_all_data():
    servicos = api_client.get("/api/servicos/").json() if api_client.get("/api/servicos/").status_code == 200 else []
    
    clientes = api_client.get("/api/clientes/").json() if api_client.get("/api/clientes/").status_code == 200 else []
    clientes_dict = {c["cliente_ID"]: c for c in clientes}
    
    carros = api_client.get("/api/carros/").json() if api_client.get("/api/carros/").status_code == 200 else []
    carros_dict = {c["carro_ID"]: c for c in carros}
    
    mecanicos = api_client.get("/api/mecanicos/").json() if api_client.get("/api/mecanicos/").status_code == 200 else []
    mecanicos_dict = {m["mecanico_ID"]: m for m in mecanicos}
    
    status = api_client.get("/api/status/").json() if api_client.get("/api/status/").status_code == 200 else []
    
    insumos = api_client.get("/api/insumos/").json() if api_client.get("/api/insumos/").status_code == 200 else []
    
    pagamentos = api_client.get("/api/pagamentos/").json() if api_client.get("/api/pagamentos/").status_code == 200 else []
    
    return servicos, clientes_dict, carros_dict, mecanicos_dict, status, insumos, pagamentos

def create_kanban_board(services, clients_dict, cars_dict, mechanics_dict, statuses):
    status_groups = {}
    for status in STATUS_MAPPING.keys():
        status_groups[status] = []
    
    for service in services:

        if 'status_atual' in service:
            status = service.get('status_atual', 'Cadastrado')
        else:
    
            service_id = service.get('servico_ID')
            service_statuses = [s for s in statuses if s.get('servico_ID') == service_id]
            if service_statuses:
        
                try:
                    service_statuses.sort(key=lambda x: x.get('data_atualizacao', ''), reverse=True)
                    status = service_statuses[0].get('status', 'Cadastrado')
                except:
                    status = 'Cadastrado'
            else:
                status = 'Cadastrado'
        
        if status not in status_groups:
            status = 'Cadastrado'  # Default status
        

        client_id = service.get("cliente_ID")
        client_name = clients_dict.get(client_id, {}).get("nome", "Unknown")
        

        car_id = service.get("carro_ID")
        car = cars_dict.get(car_id, {})
        car_info = f"{car.get('montadora', '')} {car.get('modelo_carro', '')} - {car.get('placa', '')}"
        

        mechanic_id = service.get("mecanico_ID")
        mechanic_name = mechanics_dict.get(mechanic_id, {}).get("nome", "Unassigned")
        

        entry_date = service.get("data_entrada", "")
        exit_date = service.get("data_saida", "")
        

        try:
            days_in_service = (datetime.strptime(exit_date, "%Y-%m-%d") - 
                              datetime.strptime(entry_date, "%Y-%m-%d")).days
            
    
            days_remaining = (datetime.strptime(exit_date, "%Y-%m-%d") - 
                             datetime.now()).days
            
    
            if days_remaining < 0:
                urgency = "overdue" 
            elif days_remaining < 2:
                urgency = "urgent"
            elif days_remaining < 5:
                urgency = "soon"
            else:
                urgency = "normal"
        except:
            days_in_service = "N/A"
            days_remaining = "N/A"
            urgency = "unknown"
        

        status_groups[status].append({
            "id": str(service.get("servico_ID", "")),
            "title": f"OS #{service.get('servico_ID', '')}",
            "status": status,
            "client": client_name,
            "car": car_info,
            "mechanic": mechanic_name,
            "entry_date": entry_date,
            "exit_date": exit_date,
            "days": days_in_service,
            "days_remaining": days_remaining,
            "urgency": urgency,
            "diagnostico": service.get("diagnostico", ""),
            "service_description": service.get("descricao_servico", "")
        })
    
    return status_groups

def display_kanban_columns(status_groups):
    column_statuses = [
        ["Cadastrado", "Aguardando Aprovação"],
        ["Aprovado", "Em Andamento"],
        ["Diagnóstico Adicional", "Aguardando Peças"],
        ["Finalizado", "Entregue", "Cancelado"]
    ]
    
    columns = st.columns(len(column_statuses))
    
    for i, col_statuses in enumerate(column_statuses):
        with columns[i]:
            for status in col_statuses:
                emoji = STATUS_MAPPING.get(status, "📋")
                
                st.markdown(f"""
                <div class="kanban-header">
                    {emoji} {status}
                </div>
                """, unsafe_allow_html=True)
                
                cards = status_groups.get(status, [])
                
                if not cards:
                    st.markdown("""
                    <div style="border: 1px dashed rgba(128, 128, 128, 0.15); 
                                border-radius: 6px;
                                padding: 15px;
                                text-align: center;
                                color: inherit;
                                opacity: 0.6;
                                margin-bottom: 15px;">
                        Nenhuma ordem de serviço
                    </div>
                    """, unsafe_allow_html=True)
                
                for card in cards:
            
                    urgency_class = ""
                    urgency_indicator = ""
                    
                    if card["urgency"] == "overdue":
                        urgency_indicator = "🔴"
                    elif card["urgency"] == "urgent":
                        urgency_indicator = "🟠"
                    elif card["urgency"] == "soon":
                        urgency_indicator = "🟡"
                        
                    with st.container(border=True):
                
                        st.markdown(f"""
                        <div class="service-title">
                            <span class="service-id">{card['title']}</span>
                            <span>{urgency_indicator}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                
                        st.markdown(f"""
                        <div class="client-name">{card['client']}</div>
                        <div class="car-info">{card['car']}</div>
                        """, unsafe_allow_html=True)
                        
                
                        desc = card['service_description']
                        if len(desc) > 60:
                            desc = desc[:57] + "..."
                        st.markdown(f"<div>{desc}</div>", unsafe_allow_html=True)
                        
                
                        st.markdown(f"""
                        <div class="service-meta">
                            <span class="date-badge">📅 {card['entry_date']}</span>
                            <span>👨‍🔧 {card['mechanic']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📋 Detalhes", key=f"details_{card['id']}_{status}", use_container_width=True):
                                st.session_state.view_service_id = card['id']
                                st.session_state.current_view = "details"
                        
                        with col2:
                            if st.button("🔄 Status", key=f"status_{card['id']}_{status}", use_container_width=True):
                                st.session_state.update_service_id = card['id']
                                st.session_state.current_status = status
                                st.session_state.current_view = "update_status"

def show_service_details(service_id, services, clients_dict, cars_dict, mechanics_dict, statuses, insumos):
    service = next((s for s in services if str(s.get("servico_ID")) == str(service_id)), None)
    
    if not service:
        st.error("Serviço não encontrado")
        return
    
    # Get related data
    client_id = service.get("cliente")
    car_id = service.get("carro")
    mechanic_id = service.get("mecanico")
    
    client = clients_dict.get(client_id, {})
    car = cars_dict.get(car_id, {})
    mechanic = mechanics_dict.get(mechanic_id, {})
    
    # Get address data if it's a home service
    api_client = APIClient()
    service_address = None
    if service.get('home_service') and service.get('service_address'):
        address_response = api_client.get(f"/api/enderecos/{service.get('service_address')}/")
        if address_response.status_code == 200:
            service_address = address_response.json()
    
    # Display service information
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📋 Informações do Serviço")
        
        # Show if it's a home service
        if service.get('home_service'):
            st.success("🏠 Serviço Domiciliar")
            
            if service_address:
                with st.container(border=True):
                    st.markdown("**📍 Endereço do Serviço:**")
                    st.markdown(f"{service_address.get('rua', '')}, {service_address.get('numero', '')}")
                    if service_address.get('complemento'):
                        st.markdown(f"Complemento: {service_address.get('complemento', '')}")
                    st.markdown(f"{service_address.get('bairro', '')} - {service_address.get('cidade', '')}/{service_address.get('estado', '')}")
                    st.markdown(f"CEP: {service_address.get('cep', '')}")
        else:
            st.info("🔧 Serviço na Oficina")
        
        st.markdown(f"<div style='padding: 10px; border-radius: 5px; background-color: transparent; border: 1px solid rgba(128, 128, 128, 0.15);'>{service.get('descricao_servico', 'N/A')}</div>", unsafe_allow_html=True)
    
    with col2:
        with st.container(border=True):
            st.markdown("#### 👤 Cliente")
            st.markdown(f"**Nome:** {client.get('nome', 'N/A')}")
            st.markdown(f"**Telefone:** {client.get('telefone', 'N/A')}")
            st.markdown(f"**Email:** {client.get('email', 'N/A')}")
        
        with st.container(border=True):
            st.markdown("#### 🚗 Veículo")
            st.markdown(f"**Modelo:** {car.get('modelo_carro', 'N/A')}")
            st.markdown(f"**Fabricante:** {car.get('montadora', 'N/A')}")
            st.markdown(f"**Placa:** {car.get('placa', 'N/A')}")
            st.markdown(f"**Ano:** {car.get('ano', 'N/A')}")
            st.markdown(f"**Combustível:** {car.get('combustivel', 'N/A')}")
        
        with st.container(border=True):
            st.markdown("#### 🧰 Mecânico")
            st.markdown(f"**Nome:** {mechanic.get('nome', 'N/A')}")
            st.markdown(f"**Telefone:** {mechanic.get('telefone', 'N/A')}")
        

        st.subheader("💰 Informações Financeiras e Datas")
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        with f_col1:
            st.metric("Orçamento", f"R$ {service.get('orcamento', 0):.2f}")
        
        with f_col2:
            st.metric("Data de Entrada", service.get("data_entrada", "N/A"))
        
        with f_col3:
            st.metric("Prazo de Entrega", service.get("data_saida", "N/A"))
        
        with f_col4:
    
            if "pagamento" in service:
                payment_id = service.get("pagamento")
                st.metric("Status Pagamento", "Pendente")
            else:
                st.metric("Status Pagamento", "Não registrado")
    
    tab1, tab2, tab3 = st.tabs(["Detalhes", "Histórico", "Status"])
    
    with tab1:
        st.markdown("### Detalhes do Serviço")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
    
            st.subheader("📋 Diagnóstico")
            st.markdown(f"<div style='padding: 10px; border-radius: 5px; background-color: transparent; border: 1px solid rgba(128, 128, 128, 0.15);'>{service.get('diagnostico', 'N/A')}</div>", unsafe_allow_html=True)
            
            st.subheader("🔧 Descrição do Serviço")
            st.markdown(f"<div style='padding: 10px; border-radius: 5px; background-color: transparent; border: 1px solid rgba(128, 128, 128, 0.15);'>{service.get('descricao_servico', 'N/A')}</div>", unsafe_allow_html=True)
        
        with col2:
    
            with st.container(border=True):
                st.markdown("#### 👤 Cliente")
                st.markdown(f"**Nome:** {client.get('nome', 'N/A')}")
                st.markdown(f"**Telefone:** {client.get('telefone', 'N/A')}")
                st.markdown(f"**Email:** {client.get('email', 'N/A')}")
            
    
            with st.container(border=True):
                st.markdown("#### 🚗 Veículo")
                st.markdown(f"**Modelo:** {car.get('modelo_carro', 'N/A')}")
                st.markdown(f"**Fabricante:** {car.get('montadora', 'N/A')}")
                st.markdown(f"**Placa:** {car.get('placa', 'N/A')}")
                st.markdown(f"**Ano:** {car.get('ano', 'N/A')}")
                st.markdown(f"**Combustível:** {car.get('combustivel', 'N/A')}")
            
    
            with st.container(border=True):
                st.markdown("#### 🧰 Mecânico")
                st.markdown(f"**Nome:** {mechanic.get('nome', 'N/A')}")
                st.markdown(f"**Telefone:** {mechanic.get('telefone', 'N/A')}")
        

        st.subheader("💰 Informações Financeiras e Datas")
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        with f_col1:
            st.metric("Orçamento", f"R$ {service.get('orcamento', 0):.2f}")
        
        with f_col2:
            st.metric("Data de Entrada", service.get("data_entrada", "N/A"))
        
        with f_col3:
            st.metric("Prazo de Entrega", service.get("data_saida", "N/A"))
        
        with f_col4:
    
            if "pagamento" in service:
                payment_id = service.get("pagamento")
                st.metric("Status Pagamento", "Pendente")
            else:
                st.metric("Status Pagamento", "Não registrado")
    
    with tab2:
        st.markdown("### 📊 Histórico de Status")
        
        if service_statuses:
    
            timeline_data = []
            
            for idx, status_record in enumerate(service_statuses):
                timeline_data.append({
                    "Status": status_record.get("status"),
                    "Data": status_record.get("data_atualizacao"),
                    "Observação": status_record.get("observacao", ""),
                    "index": idx
                })
            
    
            timeline_df = pd.DataFrame(timeline_data)
            
    
            status_chart = alt.Chart(timeline_df).mark_line(
                point=alt.OverlayMarkDef(size=100, filled=True, color='gray'),
                color='gray'
            ).encode(
                x=alt.X('index:O', axis=alt.Axis(title="Sequência de Status", labelAngle=0)),
                y=alt.Y('Status:N', title="Status", sort=None),
                tooltip=['Status', 'Data', 'Observação']
            ).properties(
                height=300
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                domainColor='lightgray',
                gridColor='lightgray'
            ).interactive()
            
            st.altair_chart(status_chart, use_container_width=True)
            
    
            status_history_df = pd.DataFrame(service_statuses)
            status_history_df = status_history_df[["data_atualizacao", "status", "observacao"]]
            status_history_df.columns = ["Data", "Status", "Observação"]
            
    
            status_history_df["Status"] = status_history_df["Status"].apply(
                lambda x: f"{STATUS_MAPPING.get(x, '📋')} {x}"
            )
            
            st.dataframe(
                status_history_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum histórico de status disponível.")
    
    with tab3:
        st.markdown("### 🔄 Atualizar Status")
        

        current_status = service.get('status_atual', 'Cadastrado')
        

        with st.form("update_status_form"):
            st.markdown(f"**Status Atual**: {STATUS_MAPPING.get(current_status, '📋')} {current_status}")
            
            new_status = st.selectbox(
                "Novo Status",
                options=list(STATUS_MAPPING.keys()),
                index=list(STATUS_MAPPING.keys()).index(current_status),
                format_func=lambda x: f"{STATUS_MAPPING.get(x, '📋')} {x}"
            )
            
            status_note = st.text_area(
                "Observação", 
                placeholder="Adicione uma observação sobre a mudança de status...",
                height=100
            )
            
            submit_btn = st.form_submit_button("Atualizar Status", use_container_width=True)
            
            if submit_btn:
                success, message = update_service_status(service_id, new_status, status_note)
                if success:
                    st.success("Status atualizado com sucesso!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Falha ao atualizar status: {message}")

# Function to update service status
def update_service_status(service_id, new_status, note=None):
    status_data = {
        "servico_ID": service_id,
        "status": new_status,
        "data_atualizacao": datetime.now().strftime("%Y-%m-%d"),
        "observacao": note or f"Status changed to {new_status}"
    }
    
    status_response = api_client.post("/api/status/", json=status_data)
    
    if status_response.status_code == 201:


        try:
    
            service_response = api_client.get(f"/api/servicos/{service_id}/")
            if service_response.status_code == 200:
                service_data = service_response.json()
        
                service_data["status_atual"] = new_status
        
                update_response = api_client.post(f"/api/servicos/{service_id}/update/", json=service_data)
                if update_response.status_code in [200, 201, 204]:
                    return True, "Status updated successfully"
            
    
    
            return True, "Status history recorded (service update may be pending)"
        except:
    
            return True, "Status history recorded but service update failed"
    else:
        return False, f"Failed to update status: {status_response.text}"

# Status update view
def show_status_update(service_id, current_status):
    st.markdown(f"### Atualizar Status da OS #{service_id}")
    st.markdown(f"Status atual: **{current_status}**")
    
    new_status = st.selectbox(
        "Selecione o novo status",
        options=list(STATUS_MAPPING.keys()),
        index=list(STATUS_MAPPING.keys()).index(current_status),
        format_func=lambda x: f"{STATUS_MAPPING.get(x, '📋')} {x}"
    )
    
    note = st.text_area("Observação", 
                       placeholder="Adicione uma observação sobre a mudança de status...",
                       height=100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.current_view = "kanban"
            st.session_state.update_service_id = None
            st.rerun()
    
    with col2:
        if st.button("Confirmar", type="primary", use_container_width=True):
            success, message = update_service_status(service_id, new_status, note)
            if success:
                st.success(message)
                time.sleep(1)
                st.session_state.current_view = "kanban"
                st.session_state.update_service_id = None
                st.rerun()
            else:
                st.error(message)

# Enhanced dashboard with better analytics
def show_dashboard(services, clients_dict, cars_dict, mechanics_dict, statuses):
    st.markdown("## Dashboard - Análise de Serviços")
    
    if not services:
        st.info("Nenhuma ordem de serviço disponível para análise.")
        return
        
    services_df = pd.DataFrame(services)
    
    if 'status_atual' not in services_df.columns:

        status_dict = {}
        for status in statuses:
            service_id = status.get('servico_ID')
            if service_id not in status_dict:
                status_dict[service_id] = {
                    'status': status.get('status', 'Cadastrado'),
                    'date': status.get('data_atualizacao', '')
                }
            elif status.get('data_atualizacao', '') > status_dict[service_id]['date']:
                status_dict[service_id] = {
                    'status': status.get('status', 'Cadastrado'),
                    'date': status.get('data_atualizacao', '')
                }
        

        services_df['status_atual'] = services_df['servico_ID'].apply(
            lambda id: status_dict.get(id, {'status': 'Cadastrado'})['status'] if id in status_dict else 'Cadastrado'
        )
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        total_services = len(services)
        st.metric("Total de Ordens", total_services)
    
    with kpi2:

        active_statuses = ['Cadastrado', 'Aguardando Aprovação', 'Aprovado', 
                          'Em Andamento', 'Diagnóstico Adicional', 'Aguardando Peças']
        
        active_services = len([s for s in services if s.get('status_atual') in active_statuses])
        st.metric("Ordens Ativas", active_services)
    
    with kpi3:

        completed = len([s for s in services if s.get('status_atual') in ['Finalizado', 'Entregue']])
        st.metric("Ordens Concluídas", completed)
    
    with kpi4:

        completed_services = [s for s in services if s.get('status_atual') in ['Finalizado', 'Entregue']]
        if completed_services:
            total_days = 0
            count = 0
            
            for service in completed_services:
                try:
                    entry = datetime.strptime(service.get('data_entrada', ''), "%Y-%m-%d")
                    exit = datetime.strptime(service.get('data_saida', ''), "%Y-%m-%d")
                    days = (exit - entry).days
                    total_days += days
                    count += 1
                except:
                    pass
            
            avg_days = round(total_days / count if count > 0 else 0)
            st.metric("Média de Dias", avg_days)
        else:
            st.metric("Média de Dias", "N/A")
    
    tab1, tab2, tab3 = st.tabs(["Status", "Mecânicos", "Histórico"])
    
    with tab1:

        status_counts = services_df['status_atual'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Quantidade']
        

        fig = px.pie(
            status_counts, 
            values='Quantidade', 
            names='Status', 
            title='Distribuição de Ordens de Serviço por Status',
            template="plotly_white",
            hole=0.4
        )
        

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            insidetextorientation='radial'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:

        if 'mecanico_ID' not in services_df.columns and 'mecanico' in services_df.columns:
            services_df['mecanico_ID'] = services_df['mecanico']
        

        if 'mecanico_ID' not in services_df.columns:
            st.warning("Campo 'mecanico' não encontrado nos dados. Usando valor padrão.")
            services_df['mecanico_ID'] = 0
        

        services_df['mecanico_nome'] = services_df['mecanico_ID'].apply(
            lambda x: mechanics_dict.get(x, {}).get('nome', 'Não atribuído')
        )
        

        mech_stats = services_df.groupby('mecanico_nome').agg({
            'servico_ID': 'count',
            'status_atual': lambda x: (x == 'Finalizado').sum() + (x == 'Entregue').sum()
        }).reset_index()
        
        mech_stats.columns = ['Mecânico', 'Total', 'Concluídos']
        mech_stats['Taxa de Conclusão'] = mech_stats['Concluídos'] / mech_stats['Total']
        mech_stats['Taxa de Conclusão'] = mech_stats['Taxa de Conclusão'].apply(lambda x: f"{x:.0%}")
        

        st.subheader("Desempenho por Mecânico")
        st.dataframe(
            mech_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Mecânico": st.column_config.TextColumn("Mecânico"),
                "Total": st.column_config.NumberColumn("Total de Ordens"),
                "Concluídos": st.column_config.NumberColumn("Ordens Concluídas"),
                "Taxa de Conclusão": st.column_config.TextColumn("Taxa de Conclusão")
            }
        )
        

        fig2 = px.bar(
            mech_stats,
            x='Mecânico',
            y=['Concluídos', 'Total'],
            title='Carga de Trabalho por Mecânico',
            barmode='overlay',
            template="plotly_white",
            color_discrete_sequence=['rgba(53, 83, 95, 0.7)', 'rgba(53, 83, 95, 0.3)']  # Transparent colors
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:

        status_df = pd.DataFrame(statuses)
        
        if not status_df.empty:
    
            print(f"Status DataFrame columns: {status_df.columns.tolist()}")
            
    
            servico_id_field = None
            for possible_field in ['servico_ID', 'servico', 'id', 'servico_id']:
                if possible_field in status_df.columns:
                    servico_id_field = possible_field
                    print(f"Found service ID field: {servico_id_field}")
                    break
            
    
            if not servico_id_field:
                st.warning("Campo ID do serviço não encontrado nos dados de status.")
                status_df['servico_ID'] = "N/A"
                servico_id_field = 'servico_ID'
            
    
            if 'data_atualizacao' in status_df.columns:
                status_df = status_df.sort_values(by='data_atualizacao', ascending=False)
            
    
            status_df['servico_ID_str'] = status_df[servico_id_field].astype(str)
            
    
            recent_status = status_df.head(20)
            
    
            if 'status' in recent_status.columns:
                recent_status['status_icon'] = recent_status['status'].apply(
                    lambda x: STATUS_MAPPING.get(x, '📋')
                )
            else:
                recent_status['status_icon'] = '📋'
                st.warning("Campo 'status' não encontrado nos dados.")
            
    
            for _, row in recent_status.iterrows():
                service_id = row['servico_ID_str']
                status_text = row.get('status', 'Desconhecido')
                status_icon = row.get('status_icon', '📋')
                observacao = row.get('observacao', '')
                date = row.get('data_atualizacao', 'Data desconhecida')
                
                with st.container(border=True):
                    cols = st.columns([1, 2, 3])
                    with cols[0]:
                        st.markdown(f"**OS #{service_id}**")
                        st.markdown(f"{date}")
                    with cols[1]:
                        st.markdown(f"**{status_icon} {status_text}**")
                    with cols[2]:
                        st.markdown(f"{observacao}")
        else:
            st.info("Nenhum histórico de status disponível.")
    
    if st.button("Voltar para o Quadro", use_container_width=True):
        st.session_state.current_view = "kanban"
        st.rerun()

# Service creation form
def show_new_service_form(clients_dict, cars_dict, mechanics_dict):
    st.markdown("## Nova Ordem de Serviço")
    
    clients = [{"id": k, "name": v.get("nome", "Unknown")} for k, v in clients_dict.items()]
    mechanics = [{"id": k, "name": v.get("nome", "Unknown")} for k, v in mechanics_dict.items()]
    
    # Fetch addresses data outside the form
    api_client = APIClient()
    addresses_response = api_client.get("/api/enderecos/")
    addresses_dict = {}
    if addresses_response.status_code == 200:
        addresses_data = addresses_response.json()
        addresses_dict = {addr['endereco_ID']: addr for addr in addresses_data}
    
    # Initialize session state for form data
    if 'form_client_selection' not in st.session_state:
        st.session_state.form_client_selection = "Selecione um cliente..."
    if 'form_home_service' not in st.session_state:
        st.session_state.form_home_service = False
    if 'form_address_selection' not in st.session_state:
        st.session_state.form_address_selection = None
    
    # Client selection outside form for dynamic updates
    st.markdown("### Seleção de Cliente e Veículo")
    client_options = [f"{c['name']} (ID: {c['id']})" for c in clients]
    client_selection = st.selectbox(
        "Cliente", 
        ["Selecione um cliente..."] + client_options,
        key="client_selector"
    )
    
    # Update session state
    st.session_state.form_client_selection = client_selection
    
    # Vehicle selection (dynamic based on client)
    car_selection = None
    client_id = None
    if client_selection != "Selecione um cliente...":
        client_id = int(client_selection.split("ID: ")[1].rstrip(")"))
        
        client_cars = [
            {"id": k, "info": f"{v.get('montadora', '')} {v.get('modelo_carro', '')} - {v.get('placa', '')}"}
            for k, v in cars_dict.items() 
            if v.get("Customer_ID") == client_id or v.get("cliente_ID") == client_id
        ]
        
        if client_cars:
            car_options = [f"{c['info']} (ID: {c['id']})" for c in client_cars]
            car_selection = st.selectbox(
                "Veículo", 
                ["Selecione um veículo..."] + car_options,
                key="car_selector"
            )
        else:
            st.warning("Este cliente não possui veículos cadastrados.")
    
    # Service location selection outside form
    st.markdown("### Local do Serviço")
    home_service = st.checkbox(
        "Serviço Domiciliar", 
        value=st.session_state.form_home_service,
        help="Marque se este serviço será realizado na residência do cliente",
        key="home_service_checkbox"
    )
    st.session_state.form_home_service = home_service
    
    # Address selection (dynamic based on home service and client)
    selected_address_id = None
    new_address_data = {}
    
    if home_service and client_id:
        # Get client's current address
        client_data = clients_dict.get(client_id, {})
        client_address_id = client_data.get('endereco_ID')
        
        # Create address options
        address_options = []
        if client_address_id and client_address_id in addresses_dict:
            addr = addresses_dict[client_address_id]
            address_str = f"{addr.get('rua', '')}, {addr.get('numero', '')}, {addr.get('bairro', '')} - {addr.get('cidade', '')}/{addr.get('estado', '')} (Endereço Principal)"
            address_options.append(f"{address_str} (ID: {client_address_id})")
        
        # Add option to use a different address or create new one
        address_options.extend(["Usar outro endereço...", "Cadastrar novo endereço..."])
        
        address_selection = st.selectbox(
            "Endereço para o serviço",
            address_options,
            help="Selecione o endereço onde o serviço será realizado",
            key="address_selector"
        )
        
        # Handle different address selection
        if address_selection == "Usar outro endereço...":
            # Show all available addresses
            all_address_options = []
            for addr_id, addr in addresses_dict.items():
                if addr_id != client_address_id:  # Exclude client's current address
                    addr_str = f"{addr.get('rua', '')}, {addr.get('numero', '')}, {addr.get('bairro', '')} - {addr.get('cidade', '')}/{addr.get('estado', '')}"
                    all_address_options.append(f"{addr_str} (ID: {addr_id})")
            
            if all_address_options:
                other_address_selection = st.selectbox(
                    "Selecione outro endereço",
                    ["Selecione um endereço..."] + all_address_options,
                    key="other_address_selector"
                )
                if other_address_selection != "Selecione um endereço...":
                    selected_address_id = int(other_address_selection.split("ID: ")[1].rstrip(")"))
            else:
                st.info("Nenhum outro endereço disponível. Use a opção 'Cadastrar novo endereço'.")
        
        elif address_selection == "Cadastrar novo endereço...":
            # Show form to create new address
            st.markdown("#### Novo Endereço")
            
            col1, col2 = st.columns(2)
            with col1:
                new_address_data['cep'] = st.text_input("CEP", max_chars=8, key="new_cep")
                new_address_data['rua'] = st.text_input("Rua", key="new_rua")
                new_address_data['numero'] = st.text_input("Número", key="new_numero")
                new_address_data['bairro'] = st.text_input("Bairro", key="new_bairro")
            
            with col2:
                new_address_data['complemento'] = st.text_input("Complemento (opcional)", key="new_complemento")
                new_address_data['cidade'] = st.text_input("Cidade", key="new_cidade")
                
                estados_brasileiros = [
                    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
                    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
                    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
                ]
                new_address_data['estado'] = st.selectbox("Estado", estados_brasileiros, key="new_estado")
            
            # Auto-fill from CEP if provided
            if new_address_data.get('cep') and len(new_address_data['cep']) == 8:
                if st.button("Buscar CEP", type="secondary", key="buscar_cep"):
                    try:
                        response = requests.get(f"https://viacep.com.br/ws/{new_address_data['cep']}/json/")
                        if response.status_code == 200:
                            address_data = response.json()
                            if 'erro' not in address_data:
                                st.success("CEP encontrado! Atualize a página para ver os dados preenchidos.")
                                # Store in session state for next render
                                st.session_state.cep_data = address_data
                            else:
                                st.error("CEP não encontrado.")
                    except Exception as e:
                        st.error(f"Erro ao buscar CEP: {str(e)}")
            
            # Use CEP data if available
            if 'cep_data' in st.session_state:
                cep_data = st.session_state.cep_data
                if not new_address_data.get('rua'):
                    new_address_data['rua'] = cep_data.get('logradouro', '')
                if not new_address_data.get('bairro'):
                    new_address_data['bairro'] = cep_data.get('bairro', '')
                if not new_address_data.get('cidade'):
                    new_address_data['cidade'] = cep_data.get('localidade', '')
                if not new_address_data.get('estado'):
                    new_address_data['estado'] = cep_data.get('uf', '')
        
        elif address_selection and address_selection not in ["Usar outro endereço...", "Cadastrar novo endereço..."]:
            # Extract the address ID from the selected option
            selected_address_id = int(address_selection.split("ID: ")[1].rstrip(")"))
    
    # Now the actual form with remaining fields
    with st.form("new_service_form"):
        # Mechanic selection
        mechanic_options = [f"{m['name']} (ID: {m['id']})" for m in mechanics]
        mechanic_selection = st.selectbox("Mecânico", ["Selecione um mecânico..."] + mechanic_options)
        
        # Diagnostic and service fields
        st.markdown("### Diagnóstico e Serviço")
        diagnostico = st.text_area("Diagnóstico (o que está errado)", 
                                  placeholder="Descreva os problemas identificados...",
                                  height=100)
                                  
        descricao_servico = st.text_area("Descrição do Serviço (o que será feito)", 
                                        placeholder="Descreva os serviços que serão realizados...",
                                        height=100)
        
        # Financial and date fields
        st.markdown("### Informações Financeiras")
        
        col1, col2 = st.columns(2)
        with col1:
            orcamento = st.number_input("Orçamento (R$)", min_value=0.0, step=10.0, format="%.2f")
        with col2:
            valor_total = st.number_input("Valor Total (R$)", min_value=0.0, step=10.0, format="%.2f", value=orcamento)
        
        payment_methods = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix", "Transferência", "Pendente"]
        payment_method = st.selectbox("Método de Pagamento", payment_methods)
        payment_status = st.selectbox("Status do Pagamento", ["Pendente", "Parcial", "Pago"])
        
        st.markdown("### Datas")
        col1, col2 = st.columns(2)
        with col1:
            entry_date = st.date_input("Data de Entrada", datetime.now())
        with col2:
            exit_date = st.date_input("Data de Saída Prevista", datetime.now() + timedelta(days=3))
        
        initial_status = st.selectbox(
            "Status Inicial",
            ["Cadastrado", "Aguardando Aprovação"]
        )
        
        submitted = st.form_submit_button("Criar Ordem de Serviço", type="primary")
        
        if submitted:
            # Get the current values from session state and selectors
            current_client = st.session_state.form_client_selection
            current_home_service = st.session_state.form_home_service
            
            # Validation
            if current_client == "Selecione um cliente...":
                st.error("Por favor, selecione um cliente.")
            elif car_selection is None or car_selection == "Selecione um veículo...":
                st.error("Por favor, selecione um veículo.")
            elif mechanic_selection == "Selecione um mecânico...":
                st.error("Por favor, selecione um mecânico.")
            elif not diagnostico:
                st.error("Por favor, forneça um diagnóstico do problema.")
            elif not descricao_servico:
                st.error("Por favor, forneça uma descrição do serviço a ser realizado.")
            elif current_home_service and 'address_selector' in st.session_state and st.session_state.address_selector == "Cadastrar novo endereço..." and not all([new_address_data.get('cep'), new_address_data.get('rua'), new_address_data.get('numero'), new_address_data.get('bairro'), new_address_data.get('cidade')]):
                st.error("Por favor, preencha todos os campos obrigatórios do novo endereço.")
            else:
                # Process the form submission
                service_address_id = selected_address_id
                
                # Handle new address creation if needed
                if current_home_service and 'address_selector' in st.session_state and st.session_state.address_selector == "Cadastrar novo endereço...":
                    address_response = api_client.post("/api/enderecos/", json=new_address_data)
                    if address_response.status_code == 201:
                        address_data = address_response.json()
                        service_address_id = address_data.get("endereco_ID") or address_data.get("id")
                    else:
                        st.error(f"Falha ao criar novo endereço: {address_response.text}")
                        st.stop()
                
                # Continue with service creation
                client_id = int(current_client.split("ID: ")[1].rstrip(")"))
                car_id = int(car_selection.split("ID: ")[1].rstrip(")"))
                mechanic_id = int(mechanic_selection.split("ID: ")[1].rstrip(")"))
                
                # Create payment record
                payment_data = {
                    "valor_final": orcamento,
                    "valor_total": valor_total,
                    "metodo_pagamento": payment_method,
                    "status": payment_status
                }
                
                payment_response = api_client.post("/api/pagamentos/", json=payment_data)
                
                if payment_response.status_code == 201:
                    payment_id = payment_response.json().get("pagamento_ID")
                    
                    # Create service record
                    service_data = {
                        "cliente": client_id,
                        "carro": car_id,
                        "mecanico": mechanic_id,
                        "diagnostico": diagnostico,
                        "descricao_servico": descricao_servico,
                        "orcamento": orcamento,
                        "pagamento": payment_id,
                        "data_entrada": entry_date.strftime("%Y-%m-%d"),
                        "data_saida": exit_date.strftime("%Y-%m-%d"),
                        "status_atual": initial_status,
                        "home_service": current_home_service,
                        "service_address": service_address_id if current_home_service else None
                    }
                    
                    response = api_client.post("/api/servicos/", json=service_data)
                    
                    if response.status_code == 201:
                        service_id = response.json().get("servico_ID", 0)
                        status_data = {
                            "servico_ID": service_id,
                            "status": initial_status,
                            "data_atualizacao": datetime.now().strftime("%Y-%m-%d"),
                            "observacao": "Ordem de serviço criada"
                        }
                        
                        status_response = api_client.post("/api/status/", json=status_data)
                        
                        if status_response.status_code == 201:
                            st.success("Ordem de serviço criada com sucesso!")
                            # Clear session state
                            for key in ['form_client_selection', 'form_home_service', 'form_address_selection', 'cep_data']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            time.sleep(1)
                            st.session_state.current_view = "kanban"
                            st.rerun()
                        else:
                            st.warning(f"Ordem criada, mas falha ao registrar status: {status_response.text}")
                    else:
                        st.error(f"Falha ao criar ordem de serviço: {response.text}")
                else:
                    st.error(f"Falha ao criar registro de pagamento: {payment_response.text}")
    
    if st.button("Voltar", use_container_width=True):
        st.session_state.current_view = "kanban"
        st.rerun()

# Enhanced main application with better UI structure
def main():
    st.title("Sistema de Ordens de Serviço")
    
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "kanban"
    
    if 'view_service_id' not in st.session_state:
        st.session_state.view_service_id = None
    
    if 'update_service_id' not in st.session_state:
        st.session_state.update_service_id = None
    
    if 'current_status' not in st.session_state:
        st.session_state.current_status = None
    
    # Check admin access first
    check_admin_access()
    
    # Add logout to sidebar
    add_logout_sidebar()
    
    services, clients_dict, cars_dict, mechanics_dict, statuses, insumos, pagamentos = fetch_all_data()
    
    with st.container(border=False):
        st.markdown('<div class="fixed-content">', unsafe_allow_html=True)
        
        if st.session_state.current_view != "new_service":
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("📝 Nova Ordem de Serviço", use_container_width=True, type="primary"):
                    st.session_state.current_view = "new_service"
                    st.rerun()
            
            with col2:
                if st.button("📊 Dashboard", use_container_width=True):
                    st.session_state.current_view = "dashboard"
                    st.rerun()
            
            with col3:
                if st.button("🔄 Atualizar", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.current_view == "kanban":

        with st.container(border=False):
            st.markdown('<div class="search-container">', unsafe_allow_html=True)
            search = st.text_input("🔍 Buscar por cliente, mecânico, placa ou descrição do serviço", placeholder="Digite para filtrar...")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if search:
            filtered_services = []
            search_lower = search.lower()
            
            for service in services:
        
                client_name = clients_dict.get(service.get("cliente_ID", 0), {}).get("nome", "").lower()
                mechanic_name = mechanics_dict.get(service.get("mecanico_ID", 0), {}).get("nome", "").lower()
                car = cars_dict.get(service.get("carro_ID", 0), {})
                car_info = f"{car.get('montadora', '')} {car.get('modelo_carro', '')} {car.get('placa', '')}".lower()
                description = service.get("descricao_servico", "").lower()
                diagnostico = service.get("diagnostico", "").lower()
                
        
                if (search_lower in client_name or 
                    search_lower in mechanic_name or
                    search_lower in car_info or
                    search_lower in description or
                    search_lower in diagnostico):
                    filtered_services.append(service)
            
            if filtered_services:
                st.success(f"Encontradas {len(filtered_services)} ordens de serviço")
                services = filtered_services
            else:
                st.warning("Nenhuma ordem de serviço encontrada com os termos da busca")
        

        if services:
            status_counts = {}
            for service in services:
                status = service.get('status_atual', 'Cadastrado')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            total = len(services)
            active = sum(status_counts.get(s, 0) for s in ['Cadastrado', 'Aguardando Aprovação', 'Aprovado', 'Em Andamento'])
            
            st.markdown(f"**Total: {total} ordens | Ativas: {active} ordens**")
        

        status_groups = create_kanban_board(services, clients_dict, cars_dict, mechanics_dict, statuses)
        display_kanban_columns(status_groups)
    
    elif st.session_state.current_view == "details":
        show_service_details(
            st.session_state.view_service_id, 
            services, 
            clients_dict, 
            cars_dict, 
            mechanics_dict, 
            statuses,
            insumos
        )
    
    elif st.session_state.current_view == "update_status":
        show_status_update(
            st.session_state.update_service_id,
            st.session_state.current_status
        )
    
    elif st.session_state.current_view == "new_service":
        show_new_service_form(clients_dict, cars_dict, mechanics_dict)
    
    elif st.session_state.current_view == "dashboard":
        show_dashboard(services, clients_dict, cars_dict, mechanics_dict, statuses)

# Run the application
if __name__ == "__main__":
    main()