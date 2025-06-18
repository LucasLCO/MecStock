import streamlit as st

def check_admin_access():
    """Check if user has admin access - use this in all admin pages"""
    if not st.session_state.get('is_authenticated', False):
        st.error("❌ Acesso negado. Você precisa fazer login primeiro.")
        if st.button("← Ir para Login"):
            st.switch_page("RoleSelector.py")
        st.stop()
    
    if st.session_state.get('user_role') != 'admin':
        st.error("❌ Acesso negado. Esta página é apenas para administradores.")
        if st.button("← Voltar para suas Ordens"):
            st.switch_page("RoleSelector.py")
        st.stop()

def add_logout_sidebar():
    """Add logout functionality to sidebar"""
    with st.sidebar:
        st.markdown("### 👤 Usuário Logado")
        user_data = st.session_state.get('user_data', {})
        st.write(f"**{user_data.get('nome', 'Admin')}**")
        
        if st.session_state.get('user_role') == 'admin':
            st.write("*Administrador*")
        else:
            st.write("*Cliente*")
        
        if st.button("🚪 Sair", help="Voltar à seleção de usuário"):
            # Clear session state
            for key in ['user_role', 'user_email', 'user_data', 'is_authenticated']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("RoleSelector.py")