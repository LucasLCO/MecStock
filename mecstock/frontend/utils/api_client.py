import requests
import streamlit as st
import os

class APIClient:
    def __init__(self):
        self.base_url = os.getenv("API_URL", "http://localhost:8000")
        self.session = requests.Session()
    
    def get(self, endpoint, params=None):
        return self.session.get(f"{self.base_url}{endpoint}", params=params)
    
    def post(self, endpoint, json=None, data=None):
        return self.session.post(f"{self.base_url}{endpoint}", json=json, data=data)
    
    def put(self, endpoint, json=None, data=None):
        return self.session.put(f"{self.base_url}{endpoint}", json=json, data=data)
    
    def delete(self, endpoint):
        return self.session.delete(f"{self.base_url}{endpoint}")

BASE_URL = "http://localhost:8000/api"

def get_clientes():
    response = requests.get(f"{BASE_URL}/clientes/")
    return response.json() if response.status_code == 200 else None

def get_carros():
    response = requests.get(f"{BASE_URL}/carros/")
    return response.json() if response.status_code == 200 else None

def create_servico(data):
    response = requests.post(f"{BASE_URL}/servicos/", json=data)
    return response.json() if response.status_code == 201 else None

def update_servico(servico_id, data):
    response = requests.put(f"{BASE_URL}/servicos/{servico_id}/", json=data)
    return response.json() if response.status_code == 200 else None

def delete_servico(servico_id):
    response = requests.delete(f"{BASE_URL}/servicos/{servico_id}/")
    return response.status_code == 204

def get_pagamentos():
    response = requests.get(f"{BASE_URL}/pagamentos/")
    return response.json() if response.status_code == 200 else None

def create_pagamento(data):
    response = requests.post(f"{BASE_URL}/pagamentos/", json=data)
    return response.json() if response.status_code == 201 else None

def get_mecanicos():
    response = requests.get(f"{BASE_URL}/mecanicos/")
    return response.json() if response.status_code == 200 else None