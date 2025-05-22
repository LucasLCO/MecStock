import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
from utils.api_client import APIClient
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
from dateutil.relativedelta import relativedelta

api_client = APIClient()

st.set_page_config(
    page_title="MecStock - Dashboard Gerencial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

st.markdown("""
<style>
    .dashboard-header {
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .insight-container {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 15px;
    }
    
    .insight-title {
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .insight-value {
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    .mini-card {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 5px;
        padding: 15px;
        height: 100%;
    }
    
    .small-text {
        font-size: 0.8rem;
        opacity: 0.7;
    }
    
    .alert-card {
        background-color: rgba(255, 165, 0, 0.1);
        border: 1px solid rgba(255, 165, 0, 0.3);
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    .metric-card {
        background-color: transparent;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 5px;
        padding: 15px;
        text-align: center;
        height: 100%;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.7;
    }
    
    .dashboard-section {
        margin-bottom: 2rem;
    }
    
    /* Fix for transparent metrics */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        background-color: transparent !important;
    }
    
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricLabel"] > div,
    div[data-testid="stMetricDelta"] > div {
        background-color: transparent !important;
    }
    
    div[data-testid="metric-container"] {
        background-color: transparent !important;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 5px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_all_data():
    """Fetch all required data from the API"""
    services = api_client.get("/api/servicos/").json() if api_client.get("/api/servicos/").status_code == 200 else []
    clients = api_client.get("/api/clientes/").json() if api_client.get("/api/clientes/").status_code == 200 else []
    clients_dict = {c["cliente_ID"]: c for c in clients}
    
    cars = api_client.get("/api/carros/").json() if api_client.get("/api/carros/").status_code == 200 else []
    cars_dict = {c["carro_ID"]: c for c in cars}
    
    mechanics = api_client.get("/api/mecanicos/").json() if api_client.get("/api/mecanicos/").status_code == 200 else []
    mechanics_dict = {m["mecanico_ID"]: m for m in mechanics}
    
    statuses = api_client.get("/api/status/").json() if api_client.get("/api/status/").status_code == 200 else []
    payments = api_client.get("/api/pagamentos/").json() if api_client.get("/api/pagamentos/").status_code == 200 else []
    parts = api_client.get("/api/insumos/").json() if api_client.get("/api/insumos/").status_code == 200 else []
    
    if services:
        services = enrich_service_data(services, statuses, payments, mechanics_dict)
    
    return services, clients, cars, mechanics, statuses, payments, parts, clients_dict, cars_dict, mechanics_dict

def enrich_service_data(services, statuses, payments, mechanics_dict):
    """Add derived and computed fields to service data"""
    for service in services:

        if 'data_entrada' in service and 'data_saida' in service:
            try:
                entry_date = datetime.strptime(service.get('data_entrada', ''), "%Y-%m-%d")
                exit_date = datetime.strptime(service.get('data_saida', ''), "%Y-%m-%d")
                service['service_duration_days'] = (exit_date - entry_date).days
                
        
                if service.get('status_atual') not in ['Finalizado', 'Entregue', 'Cancelado']:
                    service['overdue'] = datetime.now() > exit_date
                else:
                    service['overdue'] = False
            except:
                service['service_duration_days'] = None
                service['overdue'] = False
        

        mechanic_id = service.get('mecanico')
        service['mechanic_name'] = mechanics_dict.get(mechanic_id, {}).get('nome', 'Desconhecido')
        

        payment_id = service.get('pagamento')
        payment_data = next((p for p in payments if p.get('pagamento_ID') == payment_id), None)
        if payment_data:
            service['payment_status'] = payment_data.get('status', 'Pendente')
            service['payment_method'] = payment_data.get('metodo_pagamento', 'Desconhecido')
            service['payment_value'] = payment_data.get('valor_final', 0)
            service['revenue'] = payment_data.get('valor_total', 0)
        else:
            service['payment_status'] = 'Desconhecido'
            service['payment_method'] = 'Desconhecido'
            service['payment_value'] = 0
            service['revenue'] = 0
            
    return services

def generate_date_range(start_date=None, end_date=None, periods=90):
    """Generate a range of dates for time series analysis"""
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=periods)
    
    return pd.date_range(start=start_date, end=end_date, freq='D')

def get_random_dates(n, start_date, end_date):
    """Generate n random dates between start_date and end_date"""
    date_range = (end_date - start_date).days
    random_days = np.random.randint(0, date_range, size=n)
    return [start_date + timedelta(days=int(day)) for day in random_days]

def calculate_financial_metrics(services, time_period=30):
    """Calculate financial KPIs and trends"""
    now = datetime.now()
    start_date = now - timedelta(days=time_period)
    
    try:
        recent_services = [s for s in services if datetime.strptime(s.get('data_entrada', '2000-01-01'), "%Y-%m-%d") >= start_date]
    except:
        recent_services = []
    
    total_revenue = sum(s.get('revenue', 0) for s in recent_services)
    
    completed_revenue = sum(s.get('revenue', 0) for s in recent_services 
                           if s.get('status_atual') in ['Finalizado', 'Entregue'])
    
    pending_revenue = sum(s.get('revenue', 0) for s in recent_services 
                         if s.get('status_atual') not in ['Finalizado', 'Entregue', 'Cancelado'])
    
    payment_pending = sum(1 for s in recent_services if s.get('payment_status') == 'Pendente')
    payment_partial = sum(1 for s in recent_services if s.get('payment_status') == 'Parcial')
    payment_completed = sum(1 for s in recent_services if s.get('payment_status') == 'Pago')
    
    payment_methods = {}
    for s in recent_services:
        method = s.get('payment_method', 'Desconhecido')
        payment_methods[method] = payment_methods.get(method, 0) + 1
    
    avg_service_value = total_revenue / len(recent_services) if recent_services else 0
    
    return {
        'total_revenue': total_revenue,
        'completed_revenue': completed_revenue,
        'pending_revenue': pending_revenue,
        'payment_pending': payment_pending,
        'payment_partial': payment_partial,
        'payment_completed': payment_completed,
        'payment_methods': payment_methods,
        'avg_service_value': avg_service_value
    }

def calculate_operational_metrics(services, mechanics):
    """Calculate operational KPIs related to service efficiency"""
    active_statuses = ['Cadastrado', 'Aguardando Aprovação', 'Aprovado', 
                      'Em Andamento', 'Diagnóstico Adicional', 'Aguardando Peças']
    active_services = [s for s in services if s.get('status_atual') in active_statuses]
    
    completed_services = [s for s in services if s.get('status_atual') in ['Finalizado', 'Entregue']]
    
    overdue_services = [s for s in active_services if s.get('overdue', False)]
    
    completion_times = [s.get('service_duration_days', 0) for s in completed_services if s.get('service_duration_days')]
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    mechanic_workload = {}
    for mechanic in mechanics:
        mechanic_id = mechanic.get('mecanico_ID')
        active_count = sum(1 for s in active_services if s.get('mecanico') == mechanic_id)
        mechanic_workload[mechanic.get('nome', f'ID: {mechanic_id}')] = active_count
    
    status_distribution = {}
    for s in services:
        status = s.get('status_atual', 'Desconhecido')
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    return {
        'active_services_count': len(active_services),
        'completed_services_count': len(completed_services),
        'overdue_services_count': len(overdue_services),
        'avg_completion_time': avg_completion_time,
        'mechanic_workload': mechanic_workload,
        'status_distribution': status_distribution,
    }

def calculate_customer_metrics(services, clients, cars):
    """Calculate customer-related KPIs and insights"""
    client_service_count = {}
    for s in services:
        client_id = s.get('cliente')
        client_service_count[client_id] = client_service_count.get(client_id, 0) + 1
    
    returning_clients = {client_id for client_id, count in client_service_count.items() if count > 1}
    
    top_clients = sorted(client_service_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    car_brands = {}
    for car in cars:
        brand = car.get('montadora', 'Desconhecida')
        car_brands[brand] = car_brands.get(brand, 0) + 1
    
    return {
        'total_clients': len(clients),
        'returning_clients_count': len(returning_clients),
        'returning_clients_percentage': len(returning_clients) / len(clients) if clients else 0,
        'top_clients': top_clients,
        'car_brands': car_brands
    }

def create_revenue_trend_chart(services, time_period=90):
    """Create a time series chart of revenue trends"""
    try:

        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_period)
        

        date_revenue = []
        for s in services:
            try:
                entry_date = datetime.strptime(s.get('data_entrada', ''), "%Y-%m-%d")
                if start_date <= entry_date <= end_date:
                    date_revenue.append({
                        'date': entry_date.strftime("%Y-%m-%d"),
                        'revenue': s.get('revenue', 0)
                    })
            except:
                continue
        
        if not date_revenue:
            return None
            

        df = pd.DataFrame(date_revenue)
        df['date'] = pd.to_datetime(df['date'])
        

        daily_revenue = df.groupby(df['date'].dt.date)['revenue'].sum().reset_index()
        

        all_dates = pd.DataFrame({'date': pd.date_range(start=start_date, end=end_date, freq='D')})
        all_dates['date'] = all_dates['date'].dt.date
        

        complete_daily_revenue = pd.merge(all_dates, daily_revenue, on='date', how='left').fillna(0)
        

        complete_daily_revenue['revenue_7d_avg'] = complete_daily_revenue['revenue'].rolling(window=7, min_periods=1).mean()
        

        fig = go.Figure()
        

        fig.add_trace(go.Bar(
            x=complete_daily_revenue['date'],
            y=complete_daily_revenue['revenue'],
            name='Receita Diária',
            marker_color='rgba(72, 139, 205, 0.4)'
        ))
        

        fig.add_trace(go.Scatter(
            x=complete_daily_revenue['date'],
            y=complete_daily_revenue['revenue_7d_avg'],
            name='Média 7 dias',
            line=dict(color='rgba(72, 139, 205, 0.9)', width=2)
        ))
        

        fig.update_layout(
            title='Tendência de Receita',
            xaxis_title='Data',
            yaxis_title='Receita (R$)',
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        st.error(f"Erro ao gerar gráfico de tendência de receita: {str(e)}")
        return None

def create_mechanic_performance_chart(services, mechanics_dict):
    """Create a chart showing mechanic performance metrics"""
    try:

        mechanic_data = []
        
        for mechanic_id, mechanic in mechanics_dict.items():
            mechanic_services = [s for s in services if s.get('mecanico') == mechanic_id]
            
            if not mechanic_services:
                continue
                
            total_services = len(mechanic_services)
            completed_services = sum(1 for s in mechanic_services if s.get('status_atual') in ['Finalizado', 'Entregue'])
            avg_duration = np.mean([s.get('service_duration_days', 0) for s in mechanic_services if s.get('service_duration_days')])
            total_revenue = sum(s.get('revenue', 0) for s in mechanic_services)
            
            mechanic_data.append({
                'mechanic_name': mechanic.get('nome', f'ID: {mechanic_id}'),
                'total_services': total_services,
                'completed_services': completed_services,
                'completion_rate': completed_services / total_services if total_services > 0 else 0,
                'avg_duration': avg_duration if not np.isnan(avg_duration) else 0,
                'total_revenue': total_revenue,
                'avg_revenue': total_revenue / total_services if total_services > 0 else 0
            })
        
        if not mechanic_data:
            return None
            

        df = pd.DataFrame(mechanic_data)
        

        fig = px.bar(
            df,
            x='mechanic_name',
            y=['completed_services', 'total_services'],
            title='Desempenho por Mecânico',
            labels={
                'mechanic_name': 'Mecânico',
                'value': 'Número de Serviços',
                'variable': 'Tipo'
            },
            barmode='overlay',
            color_discrete_map={
                'completed_services': 'rgba(72, 139, 205, 0.8)',
                'total_services': 'rgba(72, 139, 205, 0.3)'
            },
            hover_data=['completion_rate', 'avg_duration', 'avg_revenue']
        )
        

        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Serviços: %{y}<br>Taxa de Conclusão: %{customdata[0]:.1%}<br>Duração Média: %{customdata[1]:.1f} dias<br>Receita Média: R$ %{customdata[2]:.2f}'
        )
        

        fig.update_layout(
            template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis={'categoryorder':'total descending'}
        )
        
        return fig
    except Exception as e:
        st.error(f"Erro ao gerar gráfico de desempenho de mecânicos: {str(e)}")
        return None

def create_status_flow_sankey(services, statuses):
    """Create a Sankey diagram showing service status flows"""
    try:

        if not statuses or len(statuses) < 2:
            return None
            

        print(f"Status data sample (first 3): {statuses[:3] if len(statuses) >= 3 else statuses}")
            

        status_transitions = {}
        

        service_statuses = {}
        for status in statuses:
    
            if not status or 'servico_ID' not in status or 'status' not in status:
                continue
                
            service_id = status.get('servico_ID')
            
    
            if service_id is None:
                continue
                
            if service_id not in service_statuses:
                service_statuses[service_id] = []
            
    
            service_statuses[service_id].append({
                'status': status.get('status', 'Desconhecido'),
                'date': status.get('data_atualizacao', '')
            })
        

        for service_id, status_list in service_statuses.items():
    
            def safe_sort_key(x):
                date_val = x.get('date')
        
                return '' if date_val is None else str(date_val)
                
            status_list.sort(key=safe_sort_key)
            
    
            for i in range(len(status_list) - 1):
                from_status = status_list[i]['status']
                to_status = status_list[i + 1]['status']
                
        
                if not from_status or not to_status:
                    continue
                    
                if (from_status, to_status) not in status_transitions:
                    status_transitions[(from_status, to_status)] = 0
                    
                status_transitions[(from_status, to_status)] += 1
        
        if not status_transitions:
            print("No valid status transitions found")
            return None
            

        all_statuses = list(set([s for s_pair in status_transitions.keys() for s in s_pair]))
        status_to_idx = {status: idx for idx, status in enumerate(all_statuses)}
        
        source = []
        target = []
        value = []
        
        for (from_status, to_status), count in status_transitions.items():
            source.append(status_to_idx[from_status])
            target.append(status_to_idx[to_status])
            value.append(count)
        

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="gray", width=0.5),
                label=all_statuses,
                color="rgba(72, 139, 205, 0.8)"
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color="rgba(72, 139, 205, 0.3)"
            )
        )])
        

        fig.update_layout(
            title="Fluxo de Status de Serviços",
            template='plotly_white',
            margin=dict(l=0, r=0, t=40, b=0),
            font=dict(size=10)
        )
        
        return fig
    except Exception as e:
        st.error(f"Erro ao gerar diagrama de fluxo de status: {str(e)}")

        import traceback
        print(f"Status flow error details: {traceback.format_exc()}")
        return None

def get_critical_alerts(services, parts):
    """Generate critical alerts for the workshop manager"""
    alerts = []
    
    overdue_services = [s for s in services if s.get('overdue', False)]
    if overdue_services:
        alerts.append({
            'severity': 'high',
            'message': f"{len(overdue_services)} serviços atrasados precisam de atenção!",
            'details': f"Serviços: {', '.join([f'#{s.get('servico_ID')}' for s in overdue_services[:5]])}" +
                      (f" e mais {len(overdue_services) - 5}..." if len(overdue_services) > 5 else "")
        })
    
    waiting_parts = [s for s in services if s.get('status_atual') == 'Aguardando Peças']
    if waiting_parts:
        alerts.append({
            'severity': 'medium',
            'message': f"{len(waiting_parts)} serviços aguardando peças",
            'details': f"Verifique o status do pedido de peças para estes serviços"
        })
    
    low_stock_parts = [p for p in parts if p.get('qtd', 0) <= p.get('estoque_minimo', 1)]
    if low_stock_parts:
        alerts.append({
            'severity': 'medium',
            'message': f"{len(low_stock_parts)} itens com estoque baixo",
            'details': f"Itens: {', '.join([p.get('nome', 'Desconhecido') for p in low_stock_parts[:3]])}" +
                      (f" e mais {len(low_stock_parts) - 3}..." if len(low_stock_parts) > 3 else "")
        })
    
    pending_approval = [s for s in services if s.get('status_atual') == 'Aguardando Aprovação']
    if pending_approval:
        alerts.append({
            'severity': 'low',
            'message': f"{len(pending_approval)} orçamentos aguardando aprovação do cliente",
            'details': f"Ligue para os clientes para confirmar os orçamentos pendentes"
        })
    
    return alerts

def get_business_insights(metrics):
    """Generate business insights based on calculated metrics"""
    insights = []
    
    if metrics['financial']['completed_revenue'] > 0:
        pending_percentage = metrics['financial']['pending_revenue'] / metrics['financial']['total_revenue'] * 100
        if pending_percentage > 30:
            insights.append({
                'title': 'Receita Pendente Alta',
                'description': f"{pending_percentage:.1f}% da receita ainda está pendente. Considere revisar processos de cobrança.",
                'metric': f"R$ {metrics['financial']['pending_revenue']:.2f}"
            })
    
    workload = metrics['operational']['mechanic_workload']
    if workload:
        max_load = max(workload.values())
        min_load = min(workload.values())
        if max_load > 2 * min_load and max_load > 3:
            overloaded = [name for name, load in workload.items() if load == max_load]
            underloaded = [name for name, load in workload.items() if load == min_load]
            insights.append({
                'title': 'Distribuição de Trabalho Desigual',
                'description': f"Mecânicos com muitos serviços: {', '.join(overloaded)}. Considere redistribuir os serviços.",
                'metric': f"{max_load} vs {min_load} serviços"
            })
    
    avg_time = metrics['operational']['avg_completion_time']
    if avg_time > 7:
        insights.append({
            'title': 'Tempo de Conclusão Elevado',
            'description': "O tempo médio para concluir serviços está elevado. Verifique gargalos no processo.",
            'metric': f"{avg_time:.1f} dias"
        })
    
    retention = metrics['customer']['returning_clients_percentage'] * 100
    if retention < 30:
        insights.append({
            'title': 'Baixa Taxa de Retenção',
            'description': "Poucos clientes estão retornando. Considere programas de fidelidade ou acompanhamento pós-serviço.",
            'metric': f"{retention:.1f}%"
        })
    
    return insights

def render_alerts(alerts):
    """Render alert cards in the dashboard"""
    if not alerts:
        st.info("Nenhum alerta crítico neste momento. Todos os sistemas operando normalmente.")
        return
        
    for alert in alerts:
        color = {
            'high': 'rgba(255, 0, 0, 0.15)',
            'medium': 'rgba(255, 165, 0, 0.15)',
            'low': 'rgba(0, 0, 255, 0.15)'
        }.get(alert['severity'], 'rgba(128, 128, 128, 0.15)')
        
        icon = {
            'high': '🔴',
            'medium': '🟠',
            'low': '🔵'
        }.get(alert['severity'], 'ℹ️')
        
        st.markdown(f"""
        <div style="background-color: {color}; border-radius: 5px; padding: 10px; margin-bottom: 10px;">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 1.5rem; margin-right: 10px;">{icon}</div>
                <div>
                    <div style="font-weight: 600;">{alert['message']}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">{alert['details']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def forecast_workload(services, days_ahead=14):
    """Forecast expected workload for the coming days"""
    today = datetime.now().date()
    forecast_end = today + timedelta(days=days_ahead)
    
    daily_workload = {(today + timedelta(days=i)).strftime("%Y-%m-%d"): 0 for i in range(days_ahead)}
    
    for service in services:
        if service.get('status_atual') in ['Cadastrado', 'Aguardando Aprovação', 'Aprovado', 'Em Andamento']:
            try:
                exit_date = datetime.strptime(service.get('data_saida', ''), "%Y-%m-%d").date()
                if today <= exit_date <= forecast_end:
                    daily_workload[exit_date.strftime("%Y-%m-%d")] += 1
            except:
                continue
    
    df = pd.DataFrame([
        {"date": date, "workload": count} 
        for date, count in daily_workload.items()
    ])
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    df['day_name'] = df['date'].dt.day_name()
    df['date_label'] = df['date'].dt.strftime('%d/%m') + ' (' + df['day_name'].str[:3] + ')'
    
    fig = px.bar(
        df,
        x='date_label',
        y='workload',
        title='Previsão de Carga para os Próximos Dias',
        labels={'date_label': 'Data', 'workload': 'Serviços'},
        color_discrete_sequence=['rgba(72, 139, 205, 0.7)']
    )
    
    for i, row in df.iterrows():
        if row['day_name'] in ['Saturday', 'Sunday']:
            fig.add_shape(
                type="rect",
                xref="x",
                yref="paper",
                x0=i-0.5,
                x1=i+0.5,
                y0=0,
                y1=1,
                fillcolor="rgba(128, 128, 128, 0.1)",
                layer="below",
                line_width=0,
            )
    
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(tickangle=45),
        showlegend=False
    )
    
    return fig

def main():
    """Main dashboard function"""
    st.markdown("<h1 class='dashboard-header'>Dashboard Gerencial - MecStock</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        time_period = st.selectbox(
            "Período de Análise",
            options=[
                ("Últimos 30 dias", 30),
                ("Últimos 90 dias", 90),
                ("Último Ano", 365),
                ("Todos os Dados", 9999)
            ],
            format_func=lambda x: x[0],
            index=1
        )[1]  # Extract the day count
    
    with col3:
        refresh = st.button("🔄 Atualizar Dados", use_container_width=True)
        if refresh:
            st.cache_data.clear()
            st.rerun()
    
    services, clients, cars, mechanics, statuses, payments, parts, clients_dict, cars_dict, mechanics_dict = fetch_all_data()
    
    if not services:
        st.warning("Não há dados de serviços disponíveis. Cadastre ordens de serviço para visualizar o dashboard.")
        return
    
    financial_metrics = calculate_financial_metrics(services, time_period)
    operational_metrics = calculate_operational_metrics(services, mechanics)
    customer_metrics = calculate_customer_metrics(services, clients, cars)
    
    all_metrics = {
        'financial': financial_metrics,
        'operational': operational_metrics,
        'customer': customer_metrics
    }
    
    alerts = get_critical_alerts(services, parts)
    insights = get_business_insights(all_metrics)
    
    if alerts:
        st.markdown("### ⚠️ Alertas Críticos")
        render_alerts(alerts)
        st.markdown("---")
    
    st.markdown("### Indicadores de Desempenho Chave")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.metric(
            "Serviços Ativos", 
            operational_metrics['active_services_count'],
            delta=None
        )
    
    with kpi_col2:
        st.metric(
            "Taxa de Conclusão", 
            f"{operational_metrics['completed_services_count'] / (operational_metrics['completed_services_count'] + operational_metrics['active_services_count']) * 100:.1f}%" if operational_metrics['completed_services_count'] + operational_metrics['active_services_count'] > 0 else "N/A",
            delta=None
        )
    
    with kpi_col3:
        st.metric(
            "Tempo Médio de Serviço", 
            f"{operational_metrics['avg_completion_time']:.1f} dias",
            delta=None
        )
    
    with kpi_col4:
        st.metric(
            "Serviços Atrasados", 
            operational_metrics['overdue_services_count'],
            delta=operational_metrics['overdue_services_count'], 
            delta_color="inverse"
        )
    
    style_metric_cards()
    
    kpi2_col1, kpi2_col2, kpi2_col3, kpi2_col4 = st.columns(4)
    
    with kpi2_col1:
        st.metric(
            "Receita Total", 
            f"R$ {financial_metrics['total_revenue']:.2f}",
            delta=None
        )
    
    with kpi2_col2:
        st.metric(
            "Receita Pendente", 
            f"R$ {financial_metrics['pending_revenue']:.2f}",
            delta=None
        )
    
    with kpi2_col3:
        st.metric(
            "Valor Médio por Serviço", 
            f"R$ {financial_metrics['avg_service_value']:.2f}",
            delta=None
        )
    
    with kpi2_col4:
        st.metric(
            "Pagamentos Pendentes", 
            financial_metrics['payment_pending'],
            delta=None
        )
    
    style_metric_cards()
    
    st.markdown("### Análise Financeira")
    
    revenue_chart = create_revenue_trend_chart(services, time_period)
    if revenue_chart:
        st.plotly_chart(revenue_chart, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar o gráfico de tendência de receita.")
    
    fin_col1, fin_col2 = st.columns(2)
    
    with fin_col1:

        methods = financial_metrics['payment_methods']
        if methods:
            methods_df = pd.DataFrame([
                {"method": method, "count": count} 
                for method, count in methods.items()
            ])
            fig = px.pie(
                methods_df, 
                values='count', 
                names='method', 
                title='Métodos de Pagamento',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de métodos de pagamento.")
    
    with fin_col2:

        payment_status_data = {
            'Status': ['Pendente', 'Parcial', 'Pago'],
            'Quantidade': [
                financial_metrics['payment_pending'], 
                financial_metrics['payment_partial'], 
                financial_metrics['payment_completed']
            ]
        }
        
        status_df = pd.DataFrame(payment_status_data)
        if not status_df['Quantidade'].sum() == 0:
            fig = px.pie(
                status_df, 
                values='Quantidade', 
                names='Status', 
                title='Status de Pagamento',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de status de pagamento.")
    
    st.markdown("### Análise Operacional")
    
    mechanic_chart = create_mechanic_performance_chart(services, mechanics_dict)
    if mechanic_chart:
        st.plotly_chart(mechanic_chart, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar o gráfico de desempenho de mecânicos.")
    
    op_col1, op_col2 = st.columns(2)
    
    with op_col1:

        status_dist = operational_metrics['status_distribution']
        if status_dist:
            status_df = pd.DataFrame([
                {"status": status, "count": count} 
                for status, count in status_dist.items()
            ])
            status_df = status_df.sort_values('count', ascending=False)
            
            fig = px.bar(
                status_df, 
                x='status', 
                y='count', 
                title='Distribuição por Status',
                labels={'status': 'Status', 'count': 'Quantidade'},
                color_discrete_sequence=['rgba(72, 139, 205, 0.7)']
            )
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de distribuição de status.")
    
    with op_col2:

        forecast_fig = forecast_workload(services)
        st.plotly_chart(forecast_fig, use_container_width=True)
    
    st.markdown("### Análise de Clientes")
    
    cust_col1, cust_col2 = st.columns(2)
    
    with cust_col1:

        st.markdown("#### Retenção de Clientes")
        
        retention_col1, retention_col2 = st.columns(2)
        with retention_col1:
            st.metric(
                "Total de Clientes", 
                customer_metrics['total_clients'],
                delta=None
            )
        
        with retention_col2:
            st.metric(
                "Clientes Recorrentes", 
                customer_metrics['returning_clients_count'],
                delta=None
            )
        

        style_metric_cards()
        

        retention_pct = customer_metrics['returning_clients_percentage'] * 100
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=retention_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Taxa de Retenção", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "gray"},
                'bar': {'color': "rgba(72, 139, 205, 0.8)"},
                'steps': [
                    {'range': [0, 30], 'color': "rgba(255, 0, 0, 0.1)"},
                    {'range': [30, 70], 'color': "rgba(255, 165, 0, 0.1)"},
                    {'range': [70, 100], 'color': "rgba(0, 128, 0, 0.1)"}
                ],
                'threshold': {
                    'line': {'color': "rgba(72, 139, 205, 1)", 'width': 4},
                    'thickness': 0.75,
                    'value': retention_pct
                }
            },
            number={'suffix': "%"}
        ))
        
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with cust_col2:

        brands = customer_metrics['car_brands']
        if brands:
            brands_df = pd.DataFrame([
                {"brand": brand, "count": count} 
                for brand, count in brands.items()
            ])
            brands_df = brands_df.sort_values('count', ascending=False)
            
    
            if len(brands_df) > 10:
                top_brands = brands_df.head(9)
                others_count = brands_df.iloc[9:]['count'].sum()
                top_brands = pd.concat([
                    top_brands,
                    pd.DataFrame([{"brand": "Outros", "count": others_count}])
                ])
                brands_df = top_brands
            
            fig = px.pie(
                brands_df, 
                values='count', 
                names='brand', 
                title='Distribuição por Marca',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para gerar o gráfico de distribuição de marcas.")
    
    st.markdown("### Análise de Fluxo de Serviços")
    
    flow_chart = create_status_flow_sankey(services, statuses)
    if flow_chart:
        st.plotly_chart(flow_chart, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar o diagrama de fluxo de status.")
    
    if insights:
        st.markdown("### 💡 Insights de Negócio")
        
        insight_cols = st.columns(len(insights))
        for i, insight in enumerate(insights):
            with insight_cols[i]:
                st.markdown(f"""
                <div class="insight-container">
                    <div class="insight-title">{insight['title']}</div>
                    <div class="insight-value">{insight['metric']}</div>
                    <div class="small-text">{insight['description']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"<div class='small-text' style='text-align: center;'>Dashboard atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()