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
    
    # Endpoints that need POST
    post_endpoints = ["/v1/vinocr", "/platerecognition"]

    try:
        if path in post_endpoints:
            # API key goes in query params for POST
            query_params = {"key": api_key}
            # Body uses "image_url" for plate_image_recognition or "upload_url" for vin_ocr
            body = {}
            if path == "/platerecognition" and "upload_url" in params:
                body["upload_url"] = params["upload_url"]
            elif path == "/v1/vinocr" and "upload_url" in params:
                body["upload_url"] = params["upload_url"]

            resp = requests.post(url, json=body, params=query_params, timeout=60)
            return resp.json()
        else:
            # GET requests
            query_params = {"key": api_key, "source": "databricks"}
            query_params.update({k: v for k, v in params.items() if v})
            resp = requests.get(url, params=query_params, timeout=30)
            return resp.json()
    except Exception as e:
        return {"success": False, "network_error": True, "message": str(e)}
