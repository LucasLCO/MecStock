import streamlit as st
import pandas as pd
import requests
from utils.api_client import APIClient

st.title("Gerenciamento de Cadastros")

api_client = APIClient()

def fetch_data(endpoint):
    response = api_client.get(endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Falha ao buscar dados do endpoint {endpoint}")
        return []

tab1, tab2, tab3 = st.tabs(["Clientes", "Veículos", "Mecânicos"])

# ===== CLIENTS TAB =====
with tab1:
    st.header("Gerenciar Clientes")

    clients_data = fetch_data("/api/clientes/")
    
    if clients_data:
        df_clients = pd.DataFrame(clients_data)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("Buscar cliente", key="client_search")
        with col2:
            sort_by = st.selectbox(
                "Ordenar por", 
                ["nome", "email", "cpf", "telefone"],
                key="client_sort"
            )
        
        if search_term:
            df_clients = df_clients[
                df_clients['nome'].str.contains(search_term, case=False) | 
                df_clients['email'].str.contains(search_term, case=False) |
                df_clients['cpf'].str.contains(search_term, case=False)
            ]
        
        df_clients = df_clients.sort_values(by=sort_by)
        
        df_clients['delete'] = False
        
        edited_clients = st.data_editor(
            df_clients,
            column_config={
                "cliente_ID": st.column_config.NumberColumn(
                    "ID",
                    help="Client ID",
                    disabled=True,
                ),
                "nome": st.column_config.TextColumn(
                    "Nome",
                    help="Nome do cliente",
                ),
                "email": st.column_config.TextColumn(
                    "Email",
                    help="Email do cliente",
                ),
                "cpf": st.column_config.TextColumn(
                    "CPF",
                    help="CPF do cliente",
                ),
                "telefone": st.column_config.TextColumn(
                    "Telefone",
                    help="Telefone do cliente",
                ),
                "endereco_ID": st.column_config.NumberColumn(
                    "ID Endereço",
                    help="ID do endereço do cliente",
                    disabled=True,
                ),
                "delete": st.column_config.CheckboxColumn(
                    "Excluir",
                    help="Selecione para excluir o cliente",
                ),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
        )
        
        if st.button("Salvar Alterações", key="save_clients"):
            changes_made = False
            
            for idx, row in edited_clients.iterrows():
                if row['delete']:
                    delete_response = api_client.delete(f"/api/clientes/{row['cliente_ID']}/")
                    if delete_response.status_code == 204:
                        changes_made = True
                        st.success(f"Cliente {row['nome']} excluído com sucesso!")
                    else:
                        st.error(f"Falha ao excluir cliente {row['nome']}")
            
            for idx, row in edited_clients.iterrows():
                if not row['delete']:  # Skip rows marked for deletion
                    original_row = df_clients.loc[df_clients['cliente_ID'] == row['cliente_ID']].iloc[0]
                    
                    if (row['nome'] != original_row['nome'] or
                        row['email'] != original_row['email'] or
                        row['cpf'] != original_row['cpf'] or
                        row['telefone'] != original_row['telefone']):
                        
                        update_data = {
                            "nome": row['nome'],
                            "email": row['email'],
                            "cpf": row['cpf'],
                            "telefone": row['telefone'],
                            "endereco_ID": row['endereco_ID']
                        }
                        
                        update_response = api_client.put(
                            f"/api/clientes/{row['cliente_ID']}/",
                            json=update_data
                        )
                        
                        if update_response.status_code in [200, 201]:
                            changes_made = True
                            st.success(f"Cliente {row['nome']} atualizado com sucesso!")
                        else:
                            st.error(f"Falha ao atualizar cliente {row['nome']}")
            
            if changes_made:
                st.rerun()  # Refresh the page
    else:
        st.info("Nenhum cliente cadastrado.")

# ===== VEHICLES TAB =====
with tab2:
    st.header("Gerenciar Veículos")

    vehicles_data = fetch_data("/api/carros/")
    
    if vehicles_data:
        df_vehicles = pd.DataFrame(vehicles_data)
        
        clients_data = fetch_data("/api/clientes/")
        clients_dict = {client['cliente_ID']: client['nome'] for client in clients_data}
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("Buscar veículo", key="vehicle_search")
        with col2:
            sort_by = st.selectbox(
                "Ordenar por", 
                ["modelo_carro", "montadora", "placa", "ano"],
                key="vehicle_sort"
            )
        
        if search_term:
            df_vehicles = df_vehicles[
                df_vehicles['modelo_carro'].str.contains(search_term, case=False) | 
                df_vehicles['montadora'].str.contains(search_term, case=False) |
                df_vehicles['placa'].str.contains(search_term, case=False)
            ]
        
        df_vehicles = df_vehicles.sort_values(by=sort_by)
        
        df_vehicles['owner_name'] = df_vehicles['Customer_ID'].apply(
            lambda x: clients_dict.get(x, "Desconhecido")
        )
        
        df_vehicles['delete'] = False
        
        edited_vehicles = st.data_editor(
            df_vehicles,
            column_config={
                "carro_ID": st.column_config.NumberColumn(
                    "ID",
                    help="ID do veículo",
                    disabled=True,
                ),
                "modelo_carro": st.column_config.TextColumn(
                    "Modelo",
                    help="Modelo do veículo",
                ),
                "montadora": st.column_config.TextColumn(
                    "Montadora",
                    help="Fabricante do veículo",
                ),
                "placa": st.column_config.TextColumn(
                    "Placa",
                    help="Placa do veículo",
                ),
                "combustivel": st.column_config.SelectboxColumn(
                    "Combustível",
                    help="Tipo de combustível",
                    options=["Gasolina", "Diesel", "Etanol", "Flex", "Elétrico", "Híbrido"],
                ),
                "ano": st.column_config.NumberColumn(
                    "Ano",
                    help="Ano do veículo",
                    min_value=1900,
                    max_value=2030,
                ),
                "owner_name": st.column_config.TextColumn(
                    "Proprietário",
                    help="Nome do proprietário",
                    disabled=True,
                ),
                "Customer_ID": st.column_config.NumberColumn(
                    "ID Cliente",
                    help="ID do proprietário",
                    disabled=True,
                ),
                "delete": st.column_config.CheckboxColumn(
                    "Excluir",
                    help="Selecione para excluir o veículo",
                ),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
        )
        
        if st.button("Salvar Alterações", key="save_vehicles"):
            changes_made = False
            
            for idx, row in edited_vehicles.iterrows():
                if row['delete']:
                    delete_response = api_client.delete(f"/api/carros/{row['carro_ID']}/")
                    if delete_response.status_code == 204:
                        changes_made = True
                        st.success(f"Veículo {row['modelo_carro']} - {row['placa']} excluído com sucesso!")
                    else:
                        st.error(f"Falha ao excluir veículo {row['modelo_carro']} - {row['placa']}")
            
            for idx, row in edited_vehicles.iterrows():
                if not row['delete']:  # Skip rows marked for deletion
                    original_row = df_vehicles.loc[df_vehicles['carro_ID'] == row['carro_ID']].iloc[0]
                    
                    if (row['modelo_carro'] != original_row['modelo_carro'] or
                        row['montadora'] != original_row['montadora'] or
                        row['placa'] != original_row['placa'] or
                        row['combustivel'] != original_row['combustivel'] or
                        row['ano'] != original_row['ano']):
                        
                        update_data = {
                            "modelo_carro": row['modelo_carro'],
                            "montadora": row['montadora'],
                            "placa": row['placa'],
                            "combustivel": row['combustivel'],
                            "ano": int(row['ano']),
                            "Customer_ID": row['Customer_ID']
                        }
                        
                        update_response = api_client.put(
                            f"/api/carros/{row['carro_ID']}/",
                            json=update_data
                        )
                        
                        if update_response.status_code in [200, 201]:
                            changes_made = True
                            st.success(f"Veículo {row['modelo_carro']} - {row['placa']} atualizado com sucesso!")
                        else:
                            st.error(f"Falha ao atualizar veículo {row['modelo_carro']} - {row['placa']}")
            
            if changes_made:
                st.rerun()  # Refresh the page
    else:
        st.info("Nenhum veículo cadastrado.")

# ===== MECHANICS TAB =====
with tab3:
    st.header("Gerenciar Mecânicos")

    mechanics_data = fetch_data("/api/mecanicos/")
    
    if mechanics_data:
        df_mechanics = pd.DataFrame(mechanics_data)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("Buscar mecânico", key="mechanic_search")
        with col2:
            sort_by = st.selectbox(
                "Ordenar por", 
                ["nome", "telefone", "email"],
                key="mechanic_sort"
            )
        
        if search_term:
            df_mechanics = df_mechanics[
                df_mechanics['nome'].str.contains(search_term, case=False) | 
                df_mechanics['email'].str.contains(search_term, case=False) |
                df_mechanics['telefone'].str.contains(search_term, case=False)
            ]
        
        df_mechanics = df_mechanics.sort_values(by=sort_by)
        
        df_mechanics['delete'] = False
        
        edited_mechanics = st.data_editor(
            df_mechanics,
            column_config={
                "mecanico_ID": st.column_config.NumberColumn(
                    "ID",
                    help="ID do mecânico",
                    disabled=True,
                ),
                "nome": st.column_config.TextColumn(
                    "Nome",
                    help="Nome do mecânico",
                ),
                "telefone": st.column_config.TextColumn(
                    "Telefone",
                    help="Telefone do mecânico",
                ),
                "email": st.column_config.TextColumn(
                    "Email",
                    help="Email do mecânico",
                ),
                "delete": st.column_config.CheckboxColumn(
                    "Excluir",
                    help="Selecione para excluir o mecânico",
                ),
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
        )
        
        if st.button("Salvar Alterações", key="save_mechanics"):
            changes_made = False
            
            for idx, row in edited_mechanics.iterrows():
                if row['delete']:
                    delete_response = api_client.delete(f"/api/mecanicos/{row['mecanico_ID']}/")
                    if delete_response.status_code == 204:
                        changes_made = True
                        st.success(f"Mecânico {row['nome']} excluído com sucesso!")
                    else:
                        st.error(f"Falha ao excluir mecânico {row['nome']}")
            
            for idx, row in edited_mechanics.iterrows():
                if not row['delete']:  # Skip rows marked for deletion
                    original_row = df_mechanics.loc[df_mechanics['mecanico_ID'] == row['mecanico_ID']].iloc[0]
                    
                    if (row['nome'] != original_row['nome'] or
                        row['telefone'] != original_row['telefone'] or
                        row['email'] != original_row['email']):
                        
                        update_data = {
                            "nome": row['nome'],
                            "telefone": row['telefone'],
                            "email": row['email']
                        }
                        
                        update_response = api_client.put(
                            f"/api/mecanicos/{row['mecanico_ID']}/",
                            json=update_data
                        )
                        
                        if update_response.status_code in [200, 201]:
                            changes_made = True
                            st.success(f"Mecânico {row['nome']} atualizado com sucesso!")
                        else:
                            st.error(f"Falha ao atualizar mecânico {row['nome']}")
            
            if changes_made:
                st.rerun()  # Refresh the page
    else:
        st.info("Nenhum mecânico cadastrado.")