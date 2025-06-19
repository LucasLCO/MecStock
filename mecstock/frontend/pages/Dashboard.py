import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from utils.api_client import APIClient
from utils.auth import check_admin_access, add_logout_sidebar

# Check admin access first
check_admin_access()

st.set_page_config(
    page_title="MecStock - Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add logout sidebar
add_logout_sidebar()

# Custom CSS for dashboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dashboard header */
    .dashboard-header {
        background: linear-gradient(135deg, rgba(255,165,0,0.1) 0%, rgba(0,0,0,0.05) 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid rgba(255,165,0,0.2);
    }
    
    .welcome-text {
        font-size: 28px;
        font-weight: 700;
        color: #FFA500;
        margin-bottom: 8px;
    }
    
    .subtitle-text {
        font-size: 16px;
        opacity: 0.8;
        margin-bottom: 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255,165,0,0.3);
        background: rgba(255,165,0,0.05);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #FFA500;
        margin-bottom: 8px;
    }
    
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        opacity: 0.8;
    }
    
    .metric-change {
        font-size: 12px;
        margin-top: 4px;
    }
    
    .metric-up {
        color: #4CAF50;
    }
    
    .metric-down {
        color: #f44336;
    }
    
    .metric-warning {
        color: #FF9800;
    }
    
    /* Chart containers */
    .chart-container {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .chart-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 16px;
        color: #FFA500;
    }
    
    /* Activity items */
    .activity-item {
        padding: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .activity-item:last-child {
        border-bottom: none;
    }
    
    .activity-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: rgba(255,165,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }
    
    .activity-content {
        flex: 1;
    }
    
    .activity-title {
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 2px;
    }
    
    .activity-time {
        font-size: 12px;
        opacity: 0.6;
    }
</style>
""", unsafe_allow_html=True)

def safe_get(data, key, default='N/A'):
    """Safely get a value from dictionary"""
    return data.get(key, default) if data else default

def get_all_data():
    """Fetch all required data from API"""
    api_client = APIClient()
    
    try:
        # Fetch all data
        services_response = api_client.get("/api/servicos/")
        clients_response = api_client.get("/api/clientes/")
        cars_response = api_client.get("/api/carros/")
        mechanics_response = api_client.get("/api/mecanicos/")
        items_response = api_client.get("/api/insumos/")
        payments_response = api_client.get("/api/pagamentos/")
        addresses_response = api_client.get("/api/enderecos/")
        
        data = {}
        is_live = True
        
        if services_response.status_code == 200:
            data['services'] = services_response.json()
        else:
            data['services'] = []
            is_live = False
            
        if clients_response.status_code == 200:
            data['clients'] = clients_response.json()
        else:
            data['clients'] = []
            is_live = False
            
        if cars_response.status_code == 200:
            data['cars'] = cars_response.json()
        else:
            data['cars'] = []
            is_live = False
            
        if mechanics_response.status_code == 200:
            data['mechanics'] = mechanics_response.json()
        else:
            data['mechanics'] = []
            
        if items_response.status_code == 200:
            data['items'] = items_response.json()
        else:
            data['items'] = []
            
        if payments_response.status_code == 200:
            data['payments'] = payments_response.json()
        else:
            data['payments'] = []
            
        if addresses_response.status_code == 200:
            data['addresses'] = addresses_response.json()
        else:
            data['addresses'] = []
        
        data['is_live'] = is_live
        return data
    
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return {
            'services': [], 'clients': [], 'cars': [], 'mechanics': [],
            'items': [], 'payments': [], 'addresses': [], 'is_live': False
        }

def create_lookup_dicts(data):
    """Create lookup dictionaries for foreign key relationships"""
    lookups = {}
    
    # Create client lookup
    lookups['clients'] = {
        client.get('cliente_ID'): client 
        for client in data['clients']
    }
    
    # Create car lookup
    lookups['cars'] = {
        car.get('carro_ID'): car 
        for car in data['cars']
    }
    
    # Create mechanic lookup
    lookups['mechanics'] = {
        mechanic.get('mecanico_ID'): mechanic 
        for mechanic in data['mechanics']
    }
    
    # Create payment lookup
    lookups['payments'] = {
        payment.get('pagamento_ID'): payment 
        for payment in data['payments']
    }
    
    # Create address lookup
    lookups['addresses'] = {
        address.get('endereco_ID'): address 
        for address in data['addresses']
    }
    
    return lookups

def enrich_services_data(services, lookups):
    """Enrich services data with related information"""
    enriched_services = []
    
    for service in services:
        enriched = service.copy()
        
        # Add client info
        client_id = service.get('cliente')
        if client_id and client_id in lookups['clients']:
            client = lookups['clients'][client_id]
            enriched['client_name'] = safe_get(client, 'nome')
            enriched['client_email'] = safe_get(client, 'email')
        
        # Add car info
        car_id = service.get('carro')
        if car_id and car_id in lookups['cars']:
            car = lookups['cars'][car_id]
            enriched['car_model'] = safe_get(car, 'modelo_carro')
            enriched['car_brand'] = safe_get(car, 'montadora')
            enriched['car_plate'] = safe_get(car, 'placa')
        
        # Add mechanic info
        mechanic_id = service.get('mecanico')
        if mechanic_id and mechanic_id in lookups['mechanics']:
            mechanic = lookups['mechanics'][mechanic_id]
            enriched['mechanic_name'] = safe_get(mechanic, 'nome')
        
        # Add payment info
        payment_id = service.get('pagamento')
        if payment_id and payment_id in lookups['payments']:
            payment = lookups['payments'][payment_id]
            enriched['payment_method'] = safe_get(payment, 'metodo_pagamento')
            enriched['payment_status'] = safe_get(payment, 'status')
            enriched['payment_total'] = safe_get(payment, 'valor_total', 0)
        
        enriched_services.append(enriched)
    
    return enriched_services

# Dashboard Header
current_time = datetime.now()
st.markdown(f"""
<div class="dashboard-header">
    <div class="welcome-text">Bem-vindo ao MecStock Dashboard</div>
    <div class="subtitle-text">
        {current_time.strftime("%A, %d de %B de %Y")} • {current_time.strftime("%H:%M")}
    </div>
</div>
""", unsafe_allow_html=True)

# Load dashboard data
with st.spinner("Carregando dados do dashboard..."):
    data = get_all_data()
    lookups = create_lookup_dicts(data)
    services = enrich_services_data(data['services'], lookups)

# Key Metrics Row
st.subheader("📊 Métricas Principais")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_services = len(services)
    services_this_week = 0
    for s in services:
        if s.get('data_entrada'):
            try:
                date_str = s['data_entrada']
                if 'T' in str(date_str):
                    service_date = datetime.fromisoformat(str(date_str).replace('Z', ''))
                else:
                    service_date = datetime.strptime(str(date_str), '%Y-%m-%d')
                
                if service_date > datetime.now() - timedelta(days=7):
                    services_this_week += 1
            except (ValueError, TypeError):
                continue
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_services}</div>
        <div class="metric-label">Ordens de Serviço</div>
        <div class="metric-change metric-up">+{services_this_week} esta semana</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_clients = len(data['clients'])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_clients}</div>
        <div class="metric-label">Clientes Ativos</div>
        <div class="metric-change metric-up">Total cadastrados</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_cars = len(data['cars'])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_cars}</div>
        <div class="metric-label">Veículos</div>
        <div class="metric-change metric-up">Total cadastrados</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    revenue = sum([float(s.get('payment_total', 0)) for s in services if s.get('payment_status') == 'Pago'])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">R${revenue:,.0f}</div>
        <div class="metric-label">Receita</div>
        <div class="metric-change metric-up">Serviços pagos</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    pending_services = len([s for s in services if s.get('status_atual') in ['Aguardando Aprovação', 'Em Andamento', 'Cadastrado']])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{pending_services}</div>
        <div class="metric-label">Serviços Pendentes</div>
        <div class="metric-change metric-warning">Requer atenção</div>
    </div>
    """, unsafe_allow_html=True)

# Data status indicator
status_col1, status_col2 = st.columns([3, 1])
with status_col2:
    if data['is_live']:
        st.markdown('<p style="text-align: right; color: #4CAF50; font-size: 12px;">🟢 Dados em tempo real</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="text-align: right; color: #FF9800; font-size: 12px;">🟡 Conectando...</p>', unsafe_allow_html=True)

st.markdown("---")

# Quick Actions Section
st.subheader("🚀 Ações Rápidas")

action_col1, action_col2, action_col3, action_col4, action_col5, action_col6 = st.columns(6)

quick_actions = [
    {"icon": "📝", "title": "Nova Ordem", "page": "pages/ordem_servico.py"},
    {"icon": "👤", "title": "Novo Cliente", "page": "pages/cadastros.py"},
    {"icon": "🚗", "title": "Novo Veículo", "page": "pages/cadastros.py"},
    {"icon": "📦", "title": "Estoque", "page": "pages/estoque.py"},
    {"icon": "💰", "title": "Financeiro", "page": "pages/financeiro.py"},
    {"icon": "📊", "title": "Relatórios", "page": "pages/relatorios.py"}
]

for i, action in enumerate(quick_actions):
    with [action_col1, action_col2, action_col3, action_col4, action_col5, action_col6][i]:
        if st.button(f"{action['icon']}\n{action['title']}", key=f"action_{i}", use_container_width=True):
            try:
                st.switch_page(action["page"])
            except:
                st.info(f"Redirecionando para {action['title']}...")

st.markdown("---")

# Charts Row
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📈 Ordens de Serviço por Status</div>', unsafe_allow_html=True)
    
    # Status distribution chart
    status_counts = {}
    for service in services:
        status = service.get('status_atual', 'Não informado')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        fig_status = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            color_discrete_sequence=['#FFA500', '#FF8C00', '#4CAF50', '#f44336', '#2196F3', '#9C27B0']
        )
        fig_status.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=300
        )
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("Nenhum dado de status disponível.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">💰 Receita dos Últimos 7 Dias</div>', unsafe_allow_html=True)
    
    # Revenue chart
    daily_revenue = {}
    for service in services:
        if service.get('data_entrada') and service.get('payment_status') == 'Pago':
            try:
                date_str = service['data_entrada']
                if 'T' in str(date_str):
                    service_date = datetime.fromisoformat(str(date_str).replace('Z', ''))
                else:
                    service_date = datetime.strptime(str(date_str), '%Y-%m-%d')
                
                date_key = service_date.date()
                if date_key > datetime.now().date() - timedelta(days=7):
                    revenue = float(service.get('payment_total', 0))
                    daily_revenue[date_key] = daily_revenue.get(date_key, 0) + revenue
            except (ValueError, TypeError):
                continue
    
    if daily_revenue:
        dates = sorted(daily_revenue.keys())
        revenues = [daily_revenue[date] for date in dates]
        
        fig_revenue = px.line(
            x=dates,
            y=revenues,
            line_shape='spline'
        )
        fig_revenue.update_traces(line_color='#FFA500', line_width=3)
        fig_revenue.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=300,
            xaxis_title="Data",
            yaxis_title="Receita (R$)"
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.info("Nenhum dado de receita dos últimos 7 dias.")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Bottom Row: Recent Activity and Pending Services
bottom_col1, bottom_col2 = st.columns(2)

with bottom_col1:
    st.subheader("📋 Serviços Pendentes")
    
    pending_services_list = [s for s in services 
                           if s.get('status_atual') in ['Aguardando Aprovação', 'Em Andamento', 'Cadastrado']][:5]
    
    if pending_services_list:
        for service in pending_services_list:
            status = service.get('status_atual', 'Não informado')
            status_color = "#FFA500" if status == 'Aguardando Aprovação' else "#4CAF50"
            
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-icon" style="background: {status_color}20; color: {status_color};">
                    🔧
                </div>
                <div class="activity-content">
                    <div class="activity-title">
                        OS #{service.get('servico_ID')} - {service.get('client_name', 'Cliente não informado')}
                    </div>
                    <div class="activity-time">
                        {status} • R${float(service.get('orcamento', 0)):,.2f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum serviço pendente no momento.")

with bottom_col2:
    st.subheader("🕒 Atividade Recente")
    
    recent_services = []
    for s in services:
        if s.get('data_entrada'):
            try:
                date_str = s['data_entrada']
                if 'T' in str(date_str):
                    service_date = datetime.fromisoformat(str(date_str).replace('Z', ''))
                else:
                    service_date = datetime.strptime(str(date_str), '%Y-%m-%d')
                
                if service_date > datetime.now() - timedelta(days=7):
                    recent_services.append({**s, 'parsed_date': service_date})
            except (ValueError, TypeError):
                continue
    
    # Sort by date and take the 5 most recent
    recent_services = sorted(recent_services, key=lambda x: x['parsed_date'], reverse=True)[:5]
    
    if recent_services:
        for service in recent_services:
            created_date = service['parsed_date']
            time_ago = datetime.now() - created_date
            
            if time_ago.days > 0:
                time_str = f"{time_ago.days} dias atrás"
            elif time_ago.seconds > 3600:
                time_str = f"{time_ago.seconds // 3600}h atrás"
            else:
                time_str = f"{time_ago.seconds // 60}min atrás"
            
            status = service.get('status_atual', 'Não informado')
            icon = "✅" if status in ['Finalizado', 'Entregue'] else "🔧"
            
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-icon">
                    {icon}
                </div>
                <div class="activity-content">
                    <div class="activity-title">
                        Nova OS #{service.get('servico_ID')} criada
                    </div>
                    <div class="activity-time">
                        {service.get('client_name', 'Cliente não informado')} • {time_str}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma atividade recente encontrada.")

# Sidebar with additional info
with st.sidebar:
    st.markdown("### 🎯 Sistema Status")
    
    st.markdown(f"""
    - **API Status**: {'🟢 Online' if data['is_live'] else '🟡 Conectando'}
    - **Última Atualização**: {datetime.now().strftime('%H:%M:%S')}
    - **Versão**: 1.0.0
    """)
    
    st.markdown("---")
    
    st.markdown("### 📞 Suporte Rápido")
    if st.button("💬 Chat Online", use_container_width=True):
        st.info("Chat de suporte em desenvolvimento")
    
    if st.button("📧 Email Suporte", use_container_width=True):
        st.info("Email: suporte@mecstock.com")
    
    st.markdown("---")
    
    st.markdown("### 🔧 Links Rápidos")
    if st.button("📝 Nova Ordem de Serviço", use_container_width=True):
        try:
            st.switch_page("pages/ordem_servico.py")
        except:
            st.info("Redirecionando...")
    
    if st.button("👥 Gerenciar Clientes", use_container_width=True):
        try:
            st.switch_page("pages/cadastros.py")
        except:
            st.info("Redirecionando...")
    
    if st.button("📦 Controle de Estoque", use_container_width=True):
        try:
            st.switch_page("pages/estoque.py")
        except:
            st.info("Redirecionando...")

# Auto-refresh functionality
if st.sidebar.button("🔄 Atualizar Dados"):
    st.rerun()

# Footer with system info
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; opacity: 0.6; font-size: 12px;">
    MecStock Dashboard • Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} • 
    {len(services)} ordens • {len(data['clients'])} clientes
</div>
""", unsafe_allow_html=True)