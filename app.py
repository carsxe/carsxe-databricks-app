import streamlit as st
from utils.helpers import validate_api_key, call_carsxe_endpoint
from utils.render_table import render_specs_table

BASE_URL = "https://api.carsxe.com"

# ===============================
# Session state defaults
# ===============================
if "api_key" not in st.session_state:
    st.session_state["api_key"] = None
if "api_key_valid" not in st.session_state:
    st.session_state["api_key_valid"] = False
if "last_response" not in st.session_state:
    st.session_state["last_response"] = None
if "last_endpoint" not in st.session_state:
    st.session_state["last_endpoint"] = None

# ===============================
# Endpoints definition
# ===============================
ENDPOINTS = {
    "Specs": {
        "path": "/specs",
        "required": ["vin"],
        "optional": ["deepdata", "disableIntVINDecoding", "format"]
    },
    "Int VIN Decoder": {
        "path": "/v1/international-vin-decoder", 
        "required": ["vin"], 
        "optional": []
    },
    "Plate Decoder": {
        "path": "/v2/platedecoder", 
        "required": ["plate", "country"], 
        "optional": ["state", "district"]
    },
    "Market Value": {
        "path": "/v2/marketvalue", 
        "required": ["vin"], 
        "optional": ["state"]
    },
    "History": {
        "path": "/history", 
        "required": ["vin"], 
        "optional": []
    },
    "Images": {
        "path": "/images",
        "required": ["make", "model"],
        "optional": ["year", "trim", "color", "transparent", "angle", "photoType", "size", "license", "format"]
    },
    "Recalls": {
        "path": "/v1/recalls", 
        "required": ["vin"], 
        "optional": []
    },
    "Plate Image Recognition": {
        "path": "/platerecognition", 
        "required": ["upload_url"], 
        "optional": []
    },
    "VIN OCR": {
        "path": "/v1/vinocr", 
        "required": ["upload_url"], 
        "optional": []
    },
    "Year/Make/Model": {
        "path": "/v1/ymm", 
        "required": ["year", "make", "model"], 
        "optional": ["trim"]
    },
    "OBD Codes Decoder": {
        "path": "/obdcodesdecoder", 
        "required": ["code"], 
        "optional": []
    },
    "Lien and Theft": {
        "path": "/v1/lien-theft", 
        "required": ["vin"], 
        "optional": []
    },
}

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
            st.success("API key is valid! You can now call endpoints.")
            st.rerun()
        else:
            st.error("Invalid API key.")

# ===============================
# Endpoints Page
# ===============================
def endpoints_page():
    st.header("CarsXE Endpoints")

    endpoint_choice = st.selectbox("Choose endpoint", list(ENDPOINTS.keys()))
    endpoint = ENDPOINTS[endpoint_choice]

    # Reset stored response if endpoint changes
    if st.session_state["last_endpoint"] != endpoint_choice:
        st.session_state["last_response"] = None
        st.session_state["last_endpoint"] = endpoint_choice

    params = {}

    # -------- Required fields --------
    st.subheader("Required Parameters")
    for field in endpoint["required"]:
        params[field] = st.text_input(field)

    # -------- Optional fields (Dynamic Expander) --------
    if endpoint["optional"]:
        with st.expander("Optional parameters", expanded=False):
            for field in endpoint["optional"]:
                if field.lower() in ["deepdata", "disableintvindecoding"]:
                    checked = st.checkbox(f"{field}", value=False)
                    if checked:
                        params[field] = "1"
                else:
                    val = st.text_input(f"{field}")
                    if val.strip():
                        params[field] = val.strip()

    # -------- Response view --------
    view_type = st.radio(
        "Choose response view",
        ["Table", "JSON"],
        index=0,
        horizontal=True
    )

    # -------- API Call --------
    if st.button(f"Call {endpoint_choice} Endpoint"):
        missing = [f for f in endpoint["required"] if not params.get(f)]
        if missing:
            st.error(f"Please fill all required fields: {', '.join(missing)}")
        else:
            with st.spinner("Calling CarsXE API..."):
                st.session_state["last_response"] = call_carsxe_endpoint(
                    endpoint["path"], params
                )

    # -------- Render stored response --------
    if st.session_state["last_response"]:
        st.subheader("API Response")
        if view_type == "JSON":
            st.json(st.session_state["last_response"])
        else:
            render_specs_table(st.session_state["last_response"])

# ===============================
# Main
# ===============================
def run_app():
    if not st.session_state.get("api_key_valid", False):
        api_key_page()
    else:
        endpoints_page()

if __name__ == "__main__":
    run_app()
