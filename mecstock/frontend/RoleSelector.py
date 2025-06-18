import streamlit as st
import requests
from utils.api_client import APIClient

# This must be the first Streamlit command
st.set_page_config(
    page_title="MecStock - Seleção de Usuário",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

def validate_client_email(email):
    """Validate if email exists in the database"""
    try:
        api_client = APIClient()
        response = api_client.get("/api/clientes/")
        
        if response.status_code == 200:
            clients = response.json()
            for client in clients:
                if client.get('email', '').lower() == email.lower():
                    return client
        return None
    except Exception as e:
        st.error(f"Erro ao validar email: {str(e)}")
        return None

def show_role_selector():
    """Show the role selection interface"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1>🔧 MecStock</h1>
        <h3>Sistema de Gestão de Oficina Mecânica</h3>
        <p>Selecione o tipo de acesso para continuar</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Selecione seu tipo de acesso:")
        
        role_choice = st.radio(
            "Tipo de usuário:",
            ["👤 Cliente", "⚙️ Administrador"],
            index=None,
            help="Selecione Cliente para ver suas ordens de serviço ou Administrador para acesso completo ao sistema"
        )
        
        if role_choice == "👤 Cliente":
            st.markdown("---")
            st.markdown("#### Acesso do Cliente")
            
            with st.form("client_login"):
                email = st.text_input(
                    "Email cadastrado:",
                    placeholder="Digite seu email cadastrado no sistema",
                    help="Use o email que você forneceu quando trouxe seu veículo para manutenção"
                )
                
                submitted = st.form_submit_button("Acessar Minhas Ordens", type="primary", use_container_width=True)
                
                if submitted:
                    if not email:
                        st.error("Por favor, digite seu email.")
                    else:
                        with st.spinner("Validando email..."):
                            client_data = validate_client_email(email)
                            
                            if client_data:
                                # Set session state for client access
                                st.session_state.user_role = "client"
                                st.session_state.user_email = email
                                st.session_state.user_data = client_data
                                st.session_state.is_authenticated = True
                                
                                st.success(f"Bem-vindo(a), {client_data.get('nome', 'Cliente')}!")
                                st.rerun()
                            else:
                                st.error("Email não encontrado. Verifique se o email está correto ou entre em contato conosco.")
        
        elif role_choice == "⚙️ Administrador":
            st.markdown("---")
            st.markdown("#### Acesso Administrativo")
            
            if st.button("Acessar Sistema Completo", type="primary", use_container_width=True):
                # Set session state for admin access
                st.session_state.user_role = "admin"
                st.session_state.user_email = "admin"
                st.session_state.user_data = {"nome": "Administrador", "tipo": "admin"}
                st.session_state.is_authenticated = True
                
                st.success("Acesso administrativo ativado!")
                st.rerun()

def show_client_dashboard():
    """Show client-specific dashboard with their orders"""
    client_data = st.session_state.user_data
    
    st.markdown(f"# Bem-vindo(a), {client_data.get('nome', 'Cliente')}! 👋")
    
    # Logout button
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("🚪 Sair", help="Voltar à seleção de usuário"):
            # Clear session state
            for key in ['user_role', 'user_email', 'user_data', 'is_authenticated']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Get client's services
    try:
        api_client = APIClient()
        services_response = api_client.get("/api/servicos/")
        
        if services_response.status_code == 200:
            all_services = services_response.json()
            # Filter services for this client
            client_services = [
                service for service in all_services 
                if service.get('cliente') == client_data.get('cliente_ID')
            ]
            
            if client_services:
                st.markdown(f"## 📋 Suas Ordens de Serviço ({len(client_services)})")
                
                # Status summary
                status_counts = {}
                for service in client_services:
                    status = service.get('status_atual', 'Não informado')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Display status summary
                cols = st.columns(len(status_counts))
                for i, (status, count) in enumerate(status_counts.items()):
                    with cols[i]:
                        st.metric(status, count)
                
                st.markdown("---")
                
                # Display services
                for service in sorted(client_services, key=lambda x: x.get('data_entrada', ''), reverse=True):
                    status = service.get('status_atual', 'Não informado')
                    
                    # Color coding for status
                    if status in ['Finalizado', 'Entregue']:
                        status_color = "🟢"
                    elif status in ['Em Andamento', 'Aprovado']:
                        status_color = "🟡"
                    elif status in ['Aguardando Aprovação', 'Cadastrado']:
                        status_color = "🔵"
                    elif status == 'Cancelado':
                        status_color = "🔴"
                    else:
                        status_color = "⚪"
                    
                    with st.expander(f"{status_color} Ordem #{service.get('servico_ID')} - {status}", expanded=(status in ['Em Andamento', 'Aguardando Aprovação'])):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📅 Informações da Ordem:**")
                            st.write(f"**Data de Entrada:** {service.get('data_entrada', 'N/A')}")
                            st.write(f"**Data de Saída Prevista:** {service.get('data_saida', 'N/A')}")
                            st.write(f"**Status Atual:** {status}")
                            
                            if service.get('home_service'):
                                st.write("**🏠 Tipo:** Serviço Domiciliar")
                            else:
                                st.write("**🔧 Tipo:** Serviço na Oficina")
                        
                        with col2:
                            st.markdown("**💰 Informações Financeiras:**")
                            orcamento = service.get('orcamento', 0)
                            st.write(f"**Orçamento:** R$ {orcamento:.2f}")
                        
                        st.markdown("**🔍 Diagnóstico:**")
                        st.info(service.get('diagnostico', 'Não informado'))
                        
                        st.markdown("**🛠️ Descrição do Serviço:**")
                        st.success(service.get('descricao_servico', 'Não informado'))
                        
                        # Show service history/status updates if available
                        try:
                            status_response = api_client.get(f"/api/status/?servico_ID={service.get('servico_ID')}")
                            if status_response.status_code == 200:
                                status_history = status_response.json()
                                if status_history:
                                    with st.expander("📈 Histórico de Status"):
                                        for status_entry in sorted(status_history, key=lambda x: x.get('data_atualizacao', ''), reverse=True):
                                            st.write(f"**{status_entry.get('data_atualizacao')}** - {status_entry.get('status')}")
                                            if status_entry.get('observacao'):
                                                st.write(f"*{status_entry.get('observacao')}*")
                        except:
                            pass
            else:
                st.info("📭 Você ainda não possui ordens de serviço em nosso sistema.")
                st.markdown("### Entre em contato conosco para agendar um serviço!")
        else:
            st.error("Erro ao carregar suas ordens de serviço. Tente novamente mais tarde.")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

def main():
    """Main application logic"""
    initialize_session_state()
    
    # Check if user is authenticated
    if not st.session_state.is_authenticated:
        show_role_selector()
    else:
        # User is authenticated, show appropriate interface
        if st.session_state.user_role == "client":
            show_client_dashboard()
        elif st.session_state.user_role == "admin":
            # Redirect to admin dashboard
            st.markdown("# Redirecionando para o sistema administrativo...")
            st.markdown("Você será redirecionado para o dashboard administrativo.")
            # Here you would typically redirect to your main dashboard
            # For now, we'll show a message
            if st.button("Ir para Dashboard Administrativo"):
                st.switch_page("pages/Dashboard.py")

if __name__ == "__main__":
    main()