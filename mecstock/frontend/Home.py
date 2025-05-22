import streamlit as st
from datetime import datetime
import pandas as pd
from utils.api_client import APIClient
import plotly.express as px

api_client = APIClient()

st.set_page_config(
    page_title="MecStock - Sistema de Gerenciamento Automotivo",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Base styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 80px 0 60px;
        position: relative;
    }
    
    .hero-badge {
        background: rgba(128, 128, 128, 0.15);
        border-radius: 50px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 24px;
    }
    
    .hero-title {
        font-size: 64px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 24px;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 24px;
        font-weight: 400;
        max-width: 800px;
        margin: 0 auto 40px;
        line-height: 1.5;
        opacity: 0.8;
    }
    
    .hero-buttons {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-bottom: 60px;
    }
    
    .primary-button, .secondary-button {
        padding: 12px 24px;
        font-weight: 500;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
        text-align: center;
        display: inline-block;
        transition: all 0.2s ease;
    }
    
    .primary-button {
        background: rgba(255, 165, 0, 0.2);
        border: 1px solid rgba(255, 165, 0, 0.4);
    }
    
    .primary-button:hover {
        background: rgba(255, 165, 0, 0.3);
        transform: translateY(-2px);
    }
    
    .secondary-button {
        background: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    .secondary-button:hover {
        background: rgba(128, 128, 128, 0.2);
        transform: translateY(-2px);
    }
    
    /* Preview image */
    .preview-container {
        margin: 0 auto 80px;
        text-align: center;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        overflow: hidden;
        width: 90%;
    }
    
    .preview-image {
        width: 100%;
        border-radius: 8px;
    }
    
    /* Features section */
    .section-title {
        font-size: 36px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 48px;
    }
    
    .features-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
        margin-bottom: 80px;
    }
    
    .feature-card {
        border-radius: 12px;
        padding: 32px;
        background-color: transparent;
        border: 1px solid rgba(128, 128, 128, 0.15);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 36px;
        margin-bottom: 20px;
    }
    
    .feature-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    
    .feature-description {
        font-size: 16px;
        line-height: 1.6;
        opacity: 0.8;
    }
    
    /* Workflow section */
    .workflow-container {
        margin-bottom: 80px;
    }
    
    .workflow-cards {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }
    
    .workflow-card {
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        background-color: transparent;
        border: 1px solid rgba(128, 128, 128, 0.15);
    }
    
    .workflow-number {
        width: 40px;
        height: 40px;
        line-height: 40px;
        border-radius: 50%;
        background: rgba(128, 128, 128, 0.1);
        margin: 0 auto 16px;
        font-weight: 600;
    }
    
    /* Testimonials */
    .testimonials-container {
        margin-bottom: 80px;
    }
    
    .testimonial-card {
        border-radius: 12px;
        padding: 32px;
        background-color: transparent;
        border: 1px solid rgba(128, 128, 128, 0.15);
        margin-bottom: 24px;
    }
    
    .testimonial-text {
        font-size: 18px;
        line-height: 1.6;
        font-style: italic;
        margin-bottom: 20px;
    }
    
    .testimonial-author {
        font-weight: 600;
    }
    
    .testimonial-position {
        font-size: 14px;
        opacity: 0.7;
    }
    
    /* CTA section */
    .cta-container {
        text-align: center;
        padding: 60px 0;
        margin-bottom: 40px;
    }
    
    .cta-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    .cta-subtitle {
        font-size: 18px;
        max-width: 600px;
        margin: 0 auto 32px;
        opacity: 0.8;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 0;
        opacity: 0.7;
        font-size: 14px;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    /* Streamlit element overrides */
    button[kind="primary"] {
        background-color: rgba(255, 165, 0, 0.2) !important;
        border: 1px solid rgba(255, 165, 0, 0.4) !important;
        color: inherit !important;
    }
    
    button[kind="primary"]:hover {
        background-color: rgba(255, 165, 0, 0.3) !important;
    }
    
    button[kind="secondary"] {
        background-color: rgba(128, 128, 128, 0.1) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        color: inherit !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: rgba(128, 128, 128, 0.2) !important;
    }
    
    div[data-testid="stMetricValue"] {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

st.write('<style>div.block-container{padding-top:0; padding-bottom:0; max-width:100%;}</style>', 
        unsafe_allow_html=True)

st.markdown("""
<div class="hero-section">
    <div class="hero-badge">Gestão Automotiva Simplificada</div>
    <h1 class="hero-title">MecStock</h1>
    <p class="hero-subtitle">Plataforma completa para gerenciamento de oficinas mecânicas com controle de ordens de serviço, estoque, clientes e muito mais.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("Iniciar Agora", key="start_button", use_container_width=True):
        st.switch_page("pages/ordem_servico.py")
        
with col2:
    if st.button("Conheça os Recursos", key="features_button", use_container_width=True):
        st.session_state.show_features = True

st.image("https://via.placeholder.com/1200x600/1a1a1a/808080?text=MecStock+Dashboard", 
         caption="MecStock Dashboard",
         use_container_width=True)

try:
    services = api_client.get("/api/servicos/").json()
    clients = api_client.get("/api/clientes/").json()
    cars = api_client.get("/api/carros/").json()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Oficinas", "100+")
    with col2:
        st.metric("Ordens de Serviço", f"{len(services)}+")
    with col3:
        st.metric("Clientes Gerenciados", f"{len(clients)}+")
    with col4:
        st.metric("Veículos Cadastrados", f"{len(cars)}+")
        
except:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Oficinas", "100+")
    with col2:
        st.metric("Ordens de Serviço", "5,000+")
    with col3:
        st.metric("Clientes Gerenciados", "10,000+")
    with col4:
        st.metric("Veículos Cadastrados", "15,000+")

st.markdown("<h2 class='section-title'>Recursos Principais</h2>", unsafe_allow_html=True)

row1_col1, row1_col2, row1_col3 = st.columns(3)
row2_col1, row2_col2, row2_col3 = st.columns(3)

with row1_col1:
    st.markdown("## 🔧")
    st.markdown("### Ordens de Serviço")
    st.write("Crie e acompanhe ordens de serviço com interface visual Kanban. Mantenha o histórico completo de cada serviço e o status atualizado.")

with row1_col2:
    st.markdown("## 📦")
    st.markdown("### Controle de Estoque")
    st.write("Gerencie peças e materiais com controle de entrada, saída e níveis mínimos de estoque. Relatórios detalhados de utilização.")

with row1_col3:
    st.markdown("## 👥")
    st.markdown("### Gestão de Clientes")
    st.write("Cadastro completo de clientes e seus veículos. Histórico de serviços e preferências para melhorar o atendimento.")

with row2_col1:
    st.markdown("## 📱")
    st.markdown("### Interface Intuitiva")
    st.write("Experiência de usuário moderna e responsiva. Acesse o sistema de qualquer dispositivo, sem necessidade de instalação.")

with row2_col2:
    st.markdown("## 📊")
    st.markdown("### Relatórios e Análises")
    st.write("Dashboards personalizados com métricas importantes do seu negócio. Tome decisões baseadas em dados reais.")

with row2_col3:
    st.markdown("## 💰")
    st.markdown("### Controle Financeiro")
    st.write("Acompanhe pagamentos, custos e lucros de cada serviço. Visão geral das finanças da sua oficina.")

st.markdown("---")

st.markdown("<h2 class='section-title'>Como Funciona</h2>", unsafe_allow_html=True)

workflow_col1, workflow_col2, workflow_col3, workflow_col4 = st.columns(4)

with workflow_col1:
    st.markdown("### 1️⃣ Cadastro")
    st.write("Registre clientes, veículos e mecânicos no sistema")

with workflow_col2:
    st.markdown("### 2️⃣ Ordem de Serviço")
    st.write("Crie ordens detalhadas com diagnóstico e orçamento")

with workflow_col3:
    st.markdown("### 3️⃣ Execução")
    st.write("Acompanhe o status e atualizações do serviço")

with workflow_col4:
    st.markdown("### 4️⃣ Finalização")
    st.write("Registre pagamentos e entregue ao cliente")

st.markdown("---")

st.markdown("<h2 class='section-title'>O Que Nossos Clientes Dizem</h2>", unsafe_allow_html=True)

testimonial_col1, testimonial_col2 = st.columns(2)

with testimonial_col1:
    st.markdown("""
    > "Desde que implementamos o MecStock, conseguimos reduzir o tempo de atendimento em 30% e praticamente eliminamos erros de comunicação entre nossa equipe."
    
    **Ricardo Silva**  
    *Proprietário, Auto Center Express*
    """)

with testimonial_col2:
    st.markdown("""
    > "O controle visual das ordens de serviço transformou nossa oficina. Agora todos sabem exatamente o que está acontecendo e conseguimos entregar com mais rapidez."
    
    **Mariana Costa**  
    *Gerente, Mecânica Precision*
    """)

st.markdown("---")

st.markdown("<h2 class='section-title'>Pronto para transformar sua oficina?</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; max-width:600px; margin:0 auto 32px; font-size:18px;'>Comece a usar o MecStock hoje mesmo e veja a diferença que um sistema completo pode fazer.</p>", unsafe_allow_html=True)

cta_col1, cta_col2 = st.columns(2)
with cta_col1:
    if st.button("Começar Agora", key="start_now_button", use_container_width=True):
        st.switch_page("pages/ordem_servico.py")
        
with cta_col2:
    if st.button("Agendar Demonstração", key="demo_button", use_container_width=True):
        st.session_state.show_demo_form = True

if st.session_state.get("show_demo_form", False):
    with st.form("demo_form"):
        st.subheader("Agendar uma Demonstração")
        st.text_input("Nome")
        st.text_input("Email")
        st.text_input("Telefone")
        st.date_input("Data Preferencial")
        submitted = st.form_submit_button("Enviar Solicitação")
        if submitted:
            st.success("Solicitação enviada! Entraremos em contato em breve.")
            st.session_state.show_demo_form = False

st.markdown("---")
st.markdown("<p style='text-align:center; opacity:0.7; font-size:14px;'>© 2025 MecStock - Sistema de Gerenciamento para Oficinas Automotivas<br>Desenvolvido com Streamlit | Todos os direitos reservados</p>", unsafe_allow_html=True)

st.markdown("""
<script>
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
</script>
""", unsafe_allow_html=True)


st.markdown("""
<style>
    .centered-text {
        text-align: center;
        max-width: 850px;
        margin: 0 auto;
        display: block;
    }
    
    .hero-container {
        padding: 40px 20px;
        text-align: center;
    }
    
    .badge-container {
        display: flex;
        justify-content: center;
        margin-bottom: 24px;
    }
    
    .badge {
        background: rgba(128, 128, 128, 0.15);
        border-radius: 50px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    
    st.markdown('<div class="badge-container"><span class="badge">Gestão Automotiva Simplificada</span></div>', 
                unsafe_allow_html=True)
    
    st.markdown('<h1 style="font-size: 64px; font-weight: 800; margin-bottom: 24px;">MecStock</h1>', 
                unsafe_allow_html=True)
    
    st.markdown('<div class="centered-text"><p style="font-size: 24px; line-height: 1.5; opacity: 0.8;">'
                'Plataforma completa para gerenciamento de oficinas mecânicas com controle de ordens de serviço, '
                'estoque, clientes e muito mais.</p></div>', 
                unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)