import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.api_client import APIClient
import os

st.set_page_config(
    page_title="MecStock - Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
api_client = APIClient()

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
    
    /* Quick actions */
    .quick-action-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        cursor: pointer;
    }
    
    .quick-action-card:hover {
        transform: translateY(-3px);
        border-color: rgba(255,165,0,0.3);
        background: rgba(255,165,0,0.05);
    }
    
    .action-icon {
        font-size: 32px;
        margin-bottom: 8px;
    }
    
    .action-title {
        font-size: 14px;
        font-weight: 600;
        color: #FFA500;
    }
    
    /* Status indicators */
    .status-online {
        color: #4CAF50;
    }
    
    .status-offline {
        color: #f44336;
    }
    
    .status-warning {
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
    
    /* Recent activity */
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

# Fetch data with caching
@st.cache_data(ttl=60, show_spinner=False)
def fetch_dashboard_data():
    """Fetch all dashboard data"""
    try:
        # Fetch data from API
        services_response = api_client.get("/api/servicos/")
        clients_response = api_client.get("/api/clientes/")
        cars_response = api_client.get("/api/carros/")
        
        if all(r.status_code == 200 for r in [services_response, clients_response, cars_response]):
            services = services_response.json()
            clients = clients_response.json()
            cars = cars_response.json()
            
            return {
                'services': services,
                'clients': clients,
                'cars': cars,
                'is_live': True
            }
        else:
            # Mock data for demonstration
            return generate_mock_data()
            
    except Exception as e:
        return generate_mock_data()

def generate_mock_data():
    """Generate mock data for demonstration"""
    import random
    from datetime import datetime, timedelta
    
    # Generate mock services
    services = []
    statuses = ['Aguardando', 'Em Andamento', 'Concluído', 'Cancelado']
    for i in range(45):
        services.append({
            'id': i + 1,
            'cliente': f'Cliente {i + 1}',
            'veiculo': f'Veículo {i + 1}',
            'status_atual': random.choice(statuses),
            'valor': random.randint(100, 2000),
            'data_entrada': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            'data_conclusao': (datetime.now() - timedelta(days=random.randint(0, 15))).isoformat() if random.choice([True, False]) else None
        })
    
    # Generate mock clients
    clients = [{'id': i + 1, 'nome': f'Cliente {i + 1}'} for i in range(85)]
    
    # Generate mock cars
    cars = [{'id': i + 1, 'modelo': f'Modelo {i + 1}'} for i in range(120)]
    
    return {
        'services': services,
        'clients': clients,
        'cars': cars,
        'is_live': False
    }

# Load dashboard data
with st.spinner("Carregando dados do dashboard..."):
    dashboard_data = fetch_dashboard_data()

# Key Metrics Row
st.subheader("📊 Métricas Principais")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_services = len(dashboard_data['services'])
    services_this_week = len([s for s in dashboard_data['services'] 
                             if datetime.fromisoformat(s['data_entrada'].replace('Z', '')) > datetime.now() - timedelta(days=7)])
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_services}</div>
        <div class="metric-label">Ordens de Serviço</div>
        <div class="metric-change metric-up">+{services_this_week} esta semana</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_clients = len(dashboard_data['clients'])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_clients}</div>
        <div class="metric-label">Clientes Ativos</div>
        <div class="metric-change metric-up">+12 este mês</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_cars = len(dashboard_data['cars'])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_cars}</div>
        <div class="metric-label">Veículos</div>
        <div class="metric-change metric-up">+8 esta semana</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    revenue = sum([s['valor'] for s in dashboard_data['services'] if s.get('data_conclusao')])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">R${revenue:,.0f}</div>
        <div class="metric-label">Receita</div>
        <div class="metric-change metric-up">+15% vs mês anterior</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    pending_services = len([s for s in dashboard_data['services'] if s['status_atual'] in ['Aguardando', 'Em Andamento']])
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
    if dashboard_data['is_live']:
        st.markdown('<p style="text-align: right; color: #4CAF50; font-size: 12px;">🟢 Dados em tempo real</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="text-align: right; color: #FF9800; font-size: 12px;">🟡 Dados de demonstração</p>', unsafe_allow_html=True)

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
    for service in dashboard_data['services']:
        status = service['status_atual']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        fig_status = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            color_discrete_sequence=['#FFA500', '#FF8C00', '#4CAF50', '#f44336']
        )
        fig_status.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=300
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">💰 Receita dos Últimos 7 Dias</div>', unsafe_allow_html=True)
    
    # Revenue chart
    daily_revenue = {}
    for service in dashboard_data['services']:
        if service.get('data_conclusao'):
            date = datetime.fromisoformat(service['data_conclusao'].replace('Z', '')).date()
            if date > datetime.now().date() - timedelta(days=7):
                daily_revenue[date] = daily_revenue.get(date, 0) + service['valor']
    
    if daily_revenue:
        dates = list(daily_revenue.keys())
        revenues = list(daily_revenue.values())
        
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
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Bottom Row: Recent Activity and Pending Services
bottom_col1, bottom_col2 = st.columns(2)

with bottom_col1:
    st.subheader("📋 Serviços Pendentes")
    
    pending_services_list = [s for s in dashboard_data['services'] 
                           if s['status_atual'] in ['Aguardando', 'Em Andamento']][:5]
    
    if pending_services_list:
        for service in pending_services_list:
            status_color = "#FFA500" if service['status_atual'] == 'Aguardando' else "#4CAF50"
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-icon" style="background: {status_color}20; color: {status_color};">
                    🔧
                </div>
                <div class="activity-content">
                    <div class="activity-title">
                        OS #{service['id']} - {service['cliente']}
                    </div>
                    <div class="activity-time">
                        {service['status_atual']} • R${service['valor']:,.2f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum serviço pendente no momento.")

with bottom_col2:
    st.subheader("🕒 Atividade Recente")
    
    recent_services = []
    for s in dashboard_data['services']:
        if s.get('data_ententrada'):
            try:
                date_str = s['data_entrada']
                # Handle different date formats
                if 'T' in str(date_str):
                    # If it's a datetime string, parse it
                    service_date = datetime.fromisoformat(str(date_str).replace('Z', ''))
                else:
                    # If it's just a date string, parse it as date and convert to datetime
                    service_date = datetime.strptime(str(date_str), '%Y-%m-%d')
                
                # Check if service is from the last 7 days
                if service_date > datetime.now() - timedelta(days=7):
                    recent_services.append(s)
            except (ValueError, TypeError):
                # Skip services with invalid dates
                continue
    
    for service in recent_services:
        created_date = datetime.fromisoformat(service['data_entrada'].replace('Z', ''))
        time_ago = datetime.now() - created_date
        
        if time_ago.days > 0:
            time_str = f"{time_ago.days} dias atrás"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600}h atrás"
        else:
            time_str = f"{time_ago.seconds // 60}min atrás"
        
        icon = "✅" if service['status_atual'] == 'Concluído' else "🔧"
        
        st.markdown(f"""
        <div class="activity-item">
            <div class="activity-icon">
                {icon}
            </div>
            <div class="activity-content">
                <div class="activity-title">
                    Nova OS #{service['id']} criada
                </div>
                <div class="activity-time">
                    {service['cliente']} • {time_str}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Sidebar with additional info
with st.sidebar:
    st.markdown("### 🎯 Sistema Status")
    
    st.markdown(f"""
    - **API Status**: {'🟢 Online' if dashboard_data['is_live'] else '🟡 Demo'}
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
    st.markdown("""
    - [📝 Nova Ordem de Serviço](pages/ordem_servico.py)
    - [👥 Gerenciar Clientes](pages/cadastros.py)
    - [📦 Controle de Estoque](pages/estoque.py)
    - [📊 Relatórios](pages/relatorios.py)
    """)

# Auto-refresh functionality
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# Footer with system info
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; opacity: 0.6; font-size: 12px;">
    MecStock Dashboard • Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} • 
    {len(dashboard_data['services'])} ordens • {len(dashboard_data['clients'])} clientes
</div>
""", unsafe_allow_html=True)