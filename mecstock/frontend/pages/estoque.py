import streamlit as st
import requests
import pandas as pd
from streamlit_searchbox import st_searchbox
import plotly.express as px

st.title("Stock Management")

def fetch_stock_data():
    response = requests.get("http://localhost:8000/api/insumos/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch stock data.")
        return []

tab1, tab2, tab3 = st.tabs(["Stock Overview", "Add New Item", "Analytics"])

with tab1:
    stock_data = fetch_stock_data()
    
    if stock_data:

        df = pd.DataFrame(stock_data)
        

        st.subheader("Stock Items")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("Search items", "")
        with col2:
            sort_by = st.selectbox("Sort by", ["nome", "preco", "qtd"])
        

        if search_term:
            df = df[df['nome'].str.contains(search_term, case=False) | 
                   df['descricao'].str.contains(search_term, case=False)]
        
        df = df.sort_values(by=sort_by)
        

        edited_df = st.data_editor(
            df,
            column_config={
                "insumo_ID": st.column_config.NumberColumn(
                    "ID",
                    help="Stock item ID",
                    disabled=True,
                ),
                "nome": st.column_config.TextColumn(
                    "Item Name",
                    help="Name of the item",
                ),
                "preco": st.column_config.NumberColumn(
                    "Price",
                    help="Current price",
                    format="R$ %.2f",
                ),
                "qtd": st.column_config.NumberColumn(
                    "Quantity",
                    help="Available quantity",
                ),
                "descricao": st.column_config.TextColumn(
                    "Description",
                    help="Item description",
                    width="large",
                ),
                "actions": st.column_config.CheckboxColumn(
                    "Delete",
                    help="Select to delete",
                    default=False,
                )
            },
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
        )
        

        if st.button("Save Changes"):
            changes_made = False
            
    
            for idx, row in edited_df.iterrows():
                if row.get('actions', False):
                    item_id = row['insumo_ID']
                    delete_response = requests.delete(f"http://localhost:8000/api/insumos/{item_id}/")
                    if delete_response.status_code == 204:
                        changes_made = True
                    else:
                        st.error(f"Failed to delete item {row['nome']}")
            
    
            for idx, row in edited_df.iterrows():
                if not row.get('actions', False):
                    original_row = df.loc[df['insumo_ID'] == row['insumo_ID']].iloc[0]
                    
            
                    if (row['nome'] != original_row['nome'] or 
                        row['preco'] != original_row['preco'] or
                        row['qtd'] != original_row['qtd'] or
                        row['descricao'] != original_row['descricao']):
                        
                
                        update_data = {
                            "nome": row['nome'],
                            "preco": row['preco'],
                            "qtd": row['qtd'],
                            "descricao": row['descricao']
                        }
                        update_response = requests.put(
                            f"http://localhost:8000/api/insumos/{row['insumo_ID']}/",
                            json=update_data
                        )
                        
                        if update_response.status_code in [200, 201]:
                            changes_made = True
                        else:
                            st.error(f"Failed to update item {row['nome']}")
            
            if changes_made:
                st.success("Stock updated successfully!")
                st.rerun()
    else:
        st.info("No stock data available.")

with tab2:
    st.subheader("Add New Stock Item")
    with st.form(key='add_stock_form'):
        nome = st.text_input("Item Name")
        col1, col2 = st.columns(2)
        with col1:
            qtd = st.number_input("Quantity", min_value=0)
        with col2:
            preco = st.number_input("Price", min_value=0.0, format="%.2f")
        descricao = st.text_area("Description")
        submit_button = st.form_submit_button("Add Item")

        if submit_button:
            if not nome:
                st.error("Item name is required")
            else:
                new_item = {
                    "nome": nome,
                    "qtd": qtd,
                    "preco": preco,
                    "descricao": descricao
                }
                response = requests.post("http://localhost:8000/api/insumos/", json=new_item)
                if response.status_code == 201:
                    st.success("Stock item added successfully!")
            
                else:
                    st.error(f"Failed to add stock item: {response.text}")

with tab3:
    st.subheader("Stock Analytics")
    
    stock_data = fetch_stock_data()
    if stock_data:
        df = pd.DataFrame(stock_data)
        

        st.write("### Item Value Distribution")
        fig = px.histogram(df, x="preco", nbins=10, title="Price Distribution")
        st.plotly_chart(fig, use_container_width=True)
        

        st.write("### Top Items by Total Value")
        df['total_value'] = df['preco'] * df['qtd']
        top_items = df.sort_values('total_value', ascending=False).head(10)
        fig2 = px.bar(top_items, x='nome', y='total_value', title="Top Items by Value")
        st.plotly_chart(fig2, use_container_width=True)
        

        low_stock = df[df['qtd'] < 5]
        if not low_stock.empty:
            st.warning("### Low Stock Warning")
            st.dataframe(low_stock[['nome', 'qtd']], use_container_width=True)