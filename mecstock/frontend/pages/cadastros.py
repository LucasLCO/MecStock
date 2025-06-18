import streamlit as st
import requests
import json
from utils.api_client import APIClient
from utils.auth import check_admin_access, add_logout_sidebar

def cadastro_cliente_page():
    st.title("Cadastro de Cliente")
    
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    if 'cliente_data' not in st.session_state:
        st.session_state.cliente_data = {}

    if 'endereco_data' not in st.session_state:
        st.session_state.endereco_data = {}
    
    api_client = APIClient()

    if st.session_state.step == 1:
        with st.form("cliente_form"):
            st.subheader("Informações Pessoais")
            
    
            nome = st.text_input("Nome Completo", 
                                value=st.session_state.cliente_data.get('Nome', ''))
            email = st.text_input("Email", 
                                 value=st.session_state.cliente_data.get('Email', ''))
            cpf = st.text_input("CPF", 
                               value=st.session_state.cliente_data.get('CPF', ''))
            telefone = st.text_input("Telefone", 
                                    value=st.session_state.cliente_data.get('Telefone', ''))
            
            submitted = st.form_submit_button("Próximo")
            
            if submitted:
        
                if not nome or not email or not cpf or not telefone:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
            
                    st.session_state.cliente_data = {
                        'Nome': nome,
                        'Email': email,
                        'CPF': cpf,
                        'Telefone': telefone
                    }
            
                    st.session_state.step = 2
                    st.rerun()
    
    elif st.session_state.step == 2:
        with st.form("endereco_form"):
            st.subheader("Endereço")
            
            cep = st.text_input("CEP", 
                               value=st.session_state.endereco_data.get('cep', ''))
            
    
            if cep and len(cep) == 8 and cep != st.session_state.endereco_data.get('cep', ''):
                try:
            
                    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                    if response.status_code == 200:
                        address_data = response.json()
                        st.session_state.endereco_data = {
                            'cep': cep,
                            'rua': address_data.get('logradouro', ''),
                            'bairro': address_data.get('bairro', ''),
                            'cidade': address_data.get('localidade', ''),
                            'estado': address_data.get('uf', ''),
                            'complemento': address_data.get('complemento', '')
                        }
                except Exception as e:
                    st.error(f"Erro ao buscar CEP: {str(e)}")
            
            rua = st.text_input("Rua", 
                               value=st.session_state.endereco_data.get('rua', ''))
            numero = st.text_input("Número", 
                                  value=st.session_state.endereco_data.get('numero', ''))
            bairro = st.text_input("Bairro", 
                                  value=st.session_state.endereco_data.get('bairro', ''))
            complemento = st.text_input("Complemento", 
                                      value=st.session_state.endereco_data.get('complemento', ''))
            cidade = st.text_input("Cidade", 
                                  value=st.session_state.endereco_data.get('cidade', ''))

    
            estados_brasileiros = [
                "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
                "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
                "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
            ]

    
            current_estado = st.session_state.endereco_data.get('estado', '')
            
    
            default_index = estados_brasileiros.index(current_estado) if current_estado in estados_brasileiros else 0
            
            estado = st.selectbox(
                "Estado", 
                options=estados_brasileiros,
                index=default_index
            )
            
            col1, col2 = st.columns(2)
            with col1:
                back_button = st.form_submit_button("Voltar")
            with col2:
                next_button = st.form_submit_button("Próximo")
            
            if back_button:
                st.session_state.step = 1
                st.rerun()
            
            if next_button:
        
                if not cep or not rua or not numero or not bairro or not cidade or not estado:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
            
                    st.session_state.endereco_data = {
                        'cep': cep,
                        'rua': rua,
                        'numero': numero,
                        'bairro': bairro,
                        'complemento': complemento,
                        'cidade': cidade,
                        'estado': estado
                    }
            
                    st.session_state.step = 3
                    st.rerun()
    
    elif st.session_state.step == 3:

        cols = st.columns([1, 0.1, 1, 0.1, 1])
        with cols[0]:
            st.caption("Step 1")
            st.markdown("**Personal Information**")
        with cols[2]:
            st.caption("Step 2")
            st.markdown("**Address**")
        with cols[4]:
            st.caption("Step 3")
            st.markdown("**Confirmation**")
            st.progress(100)
        
        st.divider()
        st.subheader("Review Information")
        st.caption("Please verify that all information is correct before confirming.")
        

        review_container = st.container(border=True)
        
        with review_container:
            cols = st.columns(2)
            
            with cols[0]:
        
                st.markdown("#### Personal Information")
                st.divider()
                
        
                details = ""
                for key, value in st.session_state.cliente_data.items():
                    label = key.upper()
                    details += f"**{label}**: {value}  \n"

                st.markdown(details)
            
            with cols[1]:
        
                st.markdown("#### Address")
                st.divider()

                for key, value in st.session_state.endereco_data.items():
                    label = key.upper()
                    details += f"**{label}**: {value}  \n"
                st.markdown(details)

        

        st.write("")
        button_cols = st.columns([1, 3, 1])
        
        with button_cols[0]:
            if st.button("Back", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        
        with button_cols[2]:
            confirm_button = st.button("Confirm", 
                                     type="primary", 
                                     use_container_width=True)
            
            if confirm_button:
                with st.spinner("Saving information..."):
                    try:
                
                        endereco_response = api_client.post("/api/enderecos/", json=st.session_state.endereco_data)
                        
                        if endereco_response.status_code == 201:
                    
                            endereco_data = endereco_response.json()
                    
                            if "id" in endereco_data:
                                endereco_id = endereco_data["id"]
                            elif "endereco_ID" in endereco_data:
                                endereco_id = endereco_data["endereco_ID"] 
                            else:
                        
                                st.warning(f"Could not find ID in response. Available keys: {', '.join(endereco_data.keys())}")
                                endereco_id = list(endereco_data.values())[0] if endereco_data else None
                            
                    
                            cliente_data = {
                                "nome": st.session_state.cliente_data.get('Nome', ''),
                                "email": st.session_state.cliente_data.get('Email', ''),
                                "cpf": st.session_state.cliente_data.get('CPF', ''),
                                "telefone": st.session_state.cliente_data.get('Telefone', ''),
                                "endereco_ID": endereco_id  # Try without _id suffix first
                            }

                            cliente_response = api_client.post("/api/clientes/", json=cliente_data)
                            
                            if cliente_response.status_code == 201:
                        
                                st.success("Client successfully registered")

                        
                                st.write("")
                                st.write("")

                        
                                button_container = st.container(border=True)
                                
                                with button_container:
                            
                                    view_btn = st.button(
                                        "View Client Details", 
                                        key="view_client_btn", 
                                        use_container_width=True,
                                        type="secondary"
                                    )
                                    
                            
                                    st.write("")
                                    
                            
                                    new_btn = st.button(
                                        "Register New Client", 
                                        key="new_reg_btn", 
                                        use_container_width=True,
                                        type="primary"
                                    )

                        
                                if new_btn:
                            
                                    st.session_state.step = 1
                                    st.session_state.cliente_data = {}
                                    st.session_state.endereco_data = {}
                                    st.rerun()
                            else:
                                st.error(f"Error registering client: {cliente_response.text}")
                        else:
                            st.error(f"Error registering address: {endereco_response.text}")
                    except Exception as e:
                        st.error(f"Error during registration: {str(e)}")

def cadastro_carro_page():
    st.title("Cadastro de Carro")
    
    if 'carro_step' not in st.session_state:
        st.session_state.carro_step = 1
    
    if 'carro_data' not in st.session_state:
        st.session_state.carro_data = {}
    
    api_client = APIClient()
    
    clientes_response = api_client.get("/api/clientes/")
    if clientes_response.status_code != 200:
        st.error("Não foi possível carregar a lista de clientes. Verifique a conexão.")
        return
    
    clientes = clientes_response.json()
    cliente_options = [f"{cliente['nome']} (ID: {cliente['cliente_ID']})" for cliente in clientes]
    
    if st.session_state.carro_step == 1:
        with st.form("carro_form"):
            st.subheader("Informações do Veículo")
            
            modelo_carro = st.text_input("Modelo", 
                                       value=st.session_state.carro_data.get('modelo_carro', ''))
            montadora = st.text_input("Montadora", 
                                     value=st.session_state.carro_data.get('montadora', ''))
            placa = st.text_input("Placa", max_chars=10, 
                                 value=st.session_state.carro_data.get('placa', ''))
            st.caption("Máximo 10 caracteres")
            
            col1, col2 = st.columns(2)
            with col1:
                combustivel = st.selectbox(
                    "Tipo de Combustível",
                    ["Gasolina", "Diesel", "Etanol", "Flex", "Elétrico", "Híbrido"],
                    index=["Gasolina", "Diesel", "Etanol", "Flex", "Elétrico", "Híbrido"].index(
                        st.session_state.carro_data.get('combustivel', 'Gasolina')
                    )
                )
            
            with col2:
                ano = st.number_input("Ano", min_value=1900, max_value=2030, 
                                     value=st.session_state.carro_data.get('ano', 2020))
            
    
            default_index = 0
            if 'cliente_selecionado' in st.session_state.carro_data:
                try:
                    default_index = cliente_options.index(st.session_state.carro_data['cliente_selecionado']) + 1
                except:
                    default_index = 0
                    
            cliente_selecionado = st.selectbox("Proprietário", 
                                             ["Selecione um cliente..."] + cliente_options,
                                             index=default_index)
            
            submitted = st.form_submit_button("Próximo")
            
            if submitted:
        
                if modelo_carro and montadora and placa and cliente_selecionado != "Selecione um cliente...":
            
                    st.session_state.carro_data = {
                        'modelo_carro': modelo_carro,
                        'montadora': montadora,
                        'placa': placa,
                        'combustivel': combustivel,
                        'ano': ano,
                        'cliente_selecionado': cliente_selecionado,
                    }
            
                    st.session_state.carro_step = 2
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
    
    elif st.session_state.carro_step == 2:

        cols = st.columns([1, 0.2, 1])
        with cols[0]:
            st.caption("Passo 1")
            st.markdown("**Informações do Veículo**")
        with cols[2]:
            st.caption("Passo 2")
            st.markdown("**Confirmação**")
            st.progress(100)
        
        st.divider()
        st.subheader("Revise as Informações")
        st.caption("Por favor, verifique se todas as informações estão corretas antes de confirmar.")
        

        review_container = st.container(border=True)
        
        with review_container:
    
            st.markdown("#### Informações do Veículo")
            st.divider()
            
            data = st.session_state.carro_data
            
    
            cliente_nome = data.get('cliente_selecionado', '').split(" (ID:")[0]
            
    
            st.markdown(f"**Modelo**: {data.get('modelo_carro', '')}")
            st.markdown(f"**Montadora**: {data.get('montadora', '')}")
            st.markdown(f"**Placa**: {data.get('placa', '')}")
            st.markdown(f"**Combustível**: {data.get('combustivel', '')}")
            st.markdown(f"**Ano**: {data.get('ano', '')}")
            st.markdown(f"**Proprietário**: {cliente_nome}")
        

        st.write("")
        button_cols = st.columns([1, 3, 1])
        
        with button_cols[0]:
            if st.button("Voltar", use_container_width=True):
                st.session_state.carro_step = 1
                st.rerun()
        
        with button_cols[2]:
            confirm_button = st.button("Confirmar", 
                                     type="primary", 
                                     use_container_width=True)
            
            if confirm_button:
                with st.spinner("Salvando informações..."):
                    try:
                
                        cliente_id = int(st.session_state.carro_data['cliente_selecionado'].split("ID: ")[1].rstrip(")"))
                        
                
                        carro_data = {
                            "modelo_carro": st.session_state.carro_data.get('modelo_carro', ''),
                            "montadora": st.session_state.carro_data.get('montadora', ''),
                            "placa": st.session_state.carro_data.get('placa', '')[:10],
                            "combustivel": st.session_state.carro_data.get('combustivel', ''),
                            "ano": st.session_state.carro_data.get('ano', 2020),
                            "Customer_ID": cliente_id
                        }
                        
                
                        response = api_client.post("/api/carros/", json=carro_data)
                        
                        if response.status_code == 201:
                            st.success("Veículo cadastrado com sucesso!")
                            
                    
                            st.write("")
                            st.write("")
                            
                    
                            if st.button("Cadastrar Novo Veículo", use_container_width=True):
                        
                                st.session_state.carro_step = 1
                                st.session_state.carro_data = {}
                                st.rerun()
                        else:
                            st.error(f"Erro ao cadastrar veículo: {response.text}")
                    except Exception as e:
                        st.error(f"Erro durante o cadastro: {str(e)}")

def cadastro_mecanico_page():
    st.title("Cadastro de Mecânico")
    
    if 'mecanico_step' not in st.session_state:
        st.session_state.mecanico_step = 1
    
    if 'mecanico_data' not in st.session_state:
        st.session_state.mecanico_data = {}
    
    api_client = APIClient()
    
    if st.session_state.mecanico_step == 1:
        with st.form("mecanico_form"):
            st.subheader("Informações do Mecânico")
            
            nome = st.text_input("Nome Completo", 
                               value=st.session_state.mecanico_data.get('nome', ''))
            telefone = st.text_input("Telefone", 
                                   value=st.session_state.mecanico_data.get('telefone', ''))
            email = st.text_input("Email", 
                                value=st.session_state.mecanico_data.get('email', ''))
            
            submitted = st.form_submit_button("Próximo")
            
            if submitted:
        
                if nome and telefone and email:
            
                    st.session_state.mecanico_data = {
                        'nome': nome,
                        'telefone': telefone,
                        'email': email
                    }
            
                    st.session_state.mecanico_step = 2
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
    
    elif st.session_state.mecanico_step == 2:

        cols = st.columns([1, 0.2, 1])
        with cols[0]:
            st.caption("Passo 1")
            st.markdown("**Informações do Mecânico**")
        with cols[2]:
            st.caption("Passo 2")
            st.markdown("**Confirmação**")
            st.progress(100)
        
        st.divider()
        st.subheader("Revise as Informações")
        st.caption("Por favor, verifique se todas as informações estão corretas antes de confirmar.")
        

        review_container = st.container(border=True)
        
        with review_container:
            st.markdown("#### Informações do Mecânico")
            st.divider()
            
    
            data = st.session_state.mecanico_data
            st.markdown(f"**Nome**: {data.get('nome', '')}")
            st.markdown(f"**Telefone**: {data.get('telefone', '')}")
            st.markdown(f"**Email**: {data.get('email', '')}")
        

        st.write("")
        button_cols = st.columns([1, 3, 1])
        
        with button_cols[0]:
            if st.button("Voltar", use_container_width=True):
                st.session_state.mecanico_step = 1
                st.rerun()
        
        with button_cols[2]:
            confirm_button = st.button("Confirmar", 
                                     type="primary", 
                                     use_container_width=True)
            
            if confirm_button:
                with st.spinner("Salvando informações..."):
                    try:
                
                        mecanico_data = {
                            "nome": st.session_state.mecanico_data.get('nome', ''),
                            "telefone": st.session_state.mecanico_data.get('telefone', ''),
                            "email": st.session_state.mecanico_data.get('email', '')
                        }
                        
                
                        response = api_client.post("/api/mecanicos/", json=mecanico_data)
                        
                        if response.status_code == 201:
                            st.success("Mecânico cadastrado com sucesso!")
                            
                    
                            st.write("")
                            st.write("")
                            
                    
                            button_container = st.container(border=True)
                            
                            with button_container:
                        
                                new_btn = st.button(
                                    "Cadastrar Novo Mecânico", 
                                    key="new_mechanic_btn",  # Changed from "new_mec_btn"
                                    use_container_width=True
                                )
                                
                        
                                if new_btn:
                            
                                    st.session_state.mecanico_step = 1
                                    st.session_state.mecanico_data = {}
                                    st.rerun()
                        else:
                            st.error(f"Erro ao cadastrar mecânico: {response.text}")
                    except Exception as e:
                        st.error(f"Erro durante o cadastro: {str(e)}")

def main():
    check_admin_access()
    add_logout_sidebar()

    st.title("Sistema de Cadastros")
    
    tab1, tab2, tab3 = st.tabs(["Cadastro de Cliente", "Cadastro de Carro", "Cadastro de Mecânico"])
    
    with tab1:
        cadastro_cliente_page()

    with tab2:
        cadastro_carro_page()

    with tab3:
        cadastro_mecanico_page()

if __name__ == "__main__":
    main()