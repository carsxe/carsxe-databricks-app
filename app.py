import json
import streamlit as st
from dataclasses import dataclass
import requests

# ===============================
# Session state defaults
# ===============================
if "api_key" not in st.session_state:
    st.session_state["api_key"] = None
if "api_key_valid" not in st.session_state:
    st.session_state["api_key_valid"] = False

BASE_URL = "https://api.carsxe.com"

# ===============================
# Helpers
# ===============================
def validate_api_key(key: str) -> bool:
    """Validate CarsXE API key via /v1/auth/validate endpoint"""
    url = f"{BASE_URL}/v1/auth/validate"
    try:
        resp = requests.get(url, params={"key": key, "source": "databricks"}, timeout=15)
        body = resp.json()
        return body.get("success", False)
    except Exception:
        return False

def call_carsxe_endpoint(path: str, params: dict, method="GET"):
    """Call a CarsXE endpoint with the stored API key"""
    api_key = st.session_state.get("api_key")
    if not api_key:
        return {"success": False, "error": "API key missing."}

    url = f"{BASE_URL}{path}"
    query_params = {"key": api_key, "source": "databricks"}
    body_params = {}

    if method.upper() == "GET":
        query_params.update({k: v for k, v in params.items() if v})
        try:
            return requests.get(url, params=query_params, timeout=30).json()
        except Exception as e:
            return {"success": False, "network_error": True, "message": str(e)}
    else:
        body_params.update({k: v for k, v in params.items() if v})
        try:
            return requests.post(url, params=query_params, data=body_params, timeout=60).json()
        except Exception as e:
            return {"success": False, "network_error": True, "message": str(e)}

# ===============================
# API Key Page
# ===============================
def api_key_page():
    st.header("Configure CarsXE API Key")
    new_key = st.text_input("Enter your CarsXE API Key", type="password")
    if st.button("Validate API Key"):
        if not new_key.strip():
            st.error("API key cannot be empty.")
        elif validate_api_key(new_key):
            st.session_state["api_key"] = new_key
            st.session_state["api_key_valid"] = True
            st.success("API key is valid! Redirecting to Endpoints...")
            st.rerun()  # Databricks rerun
        else:
            st.error("Invalid API key.")

# ===============================
# API Endpoints Page
# ===============================
def api_page():
    st.header("CarsXE Endpoints")
    endpoint_options = {
        "Specs (VIN specs)": "/specs",
        # يمكن إضافة باقي الـ endpoints هنا لاحقاً
    }

    label = st.selectbox("Choose endpoint", list(endpoint_options.keys()))
    endpoint_key = endpoint_options[label]

    params = {}
    method = "GET"
    required_fields = []

    # ===========================
    # Specs Endpoint
    # ===========================
    if endpoint_key == "/specs":
        st.subheader("Specs – VIN specifications")

        # Required
        vin = st.text_input("VIN (required)")
        params["vin"] = vin
        required_fields = ["vin"]

        # Optional
        with st.expander("Optional parameters", expanded=False):
            deepdata = st.checkbox("Deepdata (1 = extra data, slower)", value=False)
            disable_int = st.checkbox("Disable International VIN decoding", value=False)
            format_ = st.text_input("Format (optional, e.g. json or xml)")

            if deepdata:
                params["deepdata"] = "1"
            if disable_int:
                params["disableIntVINDecoding"] = "1"
            if format_.strip():
                params["format"] = format_.strip()

    # ===========================
    # Call API Button
    # ===========================
    if st.button("Call endpoint"):
        missing = [f for f in required_fields if not str(params.get(f, "")).strip()]
        if missing:
            st.error(f"Please fill all required fields: {', '.join(missing)}")
        else:
            with st.spinner("Calling CarsXE API..."):
                result = call_carsxe_endpoint(endpoint_key, params, method)
                st.subheader("API Response")
                st.json(result)

# ===============================
# Main
# ===============================
def run_app():
    if not st.session_state.get("api_key_valid", False):
        api_key_page()
    else:
        api_page()

if __name__ == "__main__":
    run_app()
