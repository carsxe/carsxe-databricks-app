import requests
import streamlit as st

BASE_URL = "https://api.carsxe.com"

def validate_api_key(key: str) -> bool:
    url = f"{BASE_URL}/v1/auth/validate"
    try:
        resp = requests.get(url, params={"key": key, "source": "databricks"}, timeout=15)
        body = resp.json()
        return body.get("success", False)
    except Exception:
        return False

def call_carsxe_endpoint(path: str, params: dict):
    api_key = st.session_state.get("api_key")
    if not api_key:
        return {"success": False, "error": "API key missing."}

    url = f"{BASE_URL}{path}"
    query_params = {"key": api_key, "source": "databricks"}
    query_params.update({k: v for k, v in params.items() if v})

    try:
        return requests.get(url, params=query_params, timeout=30).json()
    except Exception as e:
        return {"success": False, "network_error": True, "message": str(e)}
