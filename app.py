import json
import streamlit as st
import requests
import pandas as pd

BASE_URL = "https://api.carsxe.com"

# ===============================
# Session state defaults
# ===============================
if "api_key" not in st.session_state:
    st.session_state["api_key"] = None
if "api_key_valid" not in st.session_state:
    st.session_state["api_key_valid"] = False

# ===============================
# Helpers
# ===============================
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

def reformat(value):
    display_value = str(value)
    display_value = display_value.replace("_", " ")
    display_value = display_value.title()
    return display_value

# ===============================
# Table rendering with expanders
# ===============================
def render_specs_table(data):
    rows = []
    nested = {}

    for k, v in data.items():
        if isinstance(v, dict) or isinstance(v, list):
            nested[k] = v
        else:
            rows.append({"Attribute": reformat(k), "Value": str(v)})

    if rows:
        df = pd.DataFrame(rows)
        st.table(df)  # st.table by default doesn't show the index in Streamlit
        # لو حاب تستخدم st.dataframe مع index=False:
        # st.dataframe(df, use_container_width=True)

    for k, v in nested.items():
        with st.expander(f"{reformat(k)}"):
            if isinstance(v, dict):
                render_specs_table(v)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        with st.expander(f"Item {i+1}"):
                            render_specs_table(item)
                    else:
                        st.write(reformat(item))

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
            st.success("API key is valid! You can now call the Specs endpoint.")
            st.rerun()
        else:
            st.error("Invalid API key.")

# ===============================
# Specs Endpoint Page
# ===============================
def specs_page():
    st.header("Specs Endpoint – VIN Specifications")

    vin = st.text_input("VIN (required)")
     # Optional parameters as dropdown
    optional_params = {
        "deepdata": "Include extra data (slower)",
        "disableIntVINDecoding": "Disable international VIN decoding",
        "format": "Response format (json/xml)"
    }

    selected_optionals = st.multiselect(
        "Optional Parameters",
        list(optional_params.keys()),
        format_func=lambda x: optional_params[x]
    )

    # Prepare params
    params = {"vin": vin}

    for key in selected_optionals:
        if key == "format":
            fmt = st.text_input("format (optional, e.g. 'json' or 'xml')", "")
            if fmt.strip():
                params[key] = fmt.strip()
        else:
            params[key] = "1"

    # Choose view type before call
    view_type = st.radio("Choose response view", ["Table", "JSON"], horizontal=True)

    # Initialize session_state for storing last result
    if "specs_result" not in st.session_state:
        st.session_state["specs_result"] = None

    if st.button("Call Specs Endpoint"):
        if not vin.strip():
            st.error("VIN is required.")
        else:
            with st.spinner("Calling CarsXE API..."):
                st.session_state["specs_result"] = call_carsxe_endpoint("/specs", params)

    # Display the stored result
    if st.session_state["specs_result"]:
        st.subheader("API Response")
        if view_type == "JSON":
            st.json(st.session_state["specs_result"])
        else:
            render_specs_table(st.session_state["specs_result"])


# ===============================
# Main
# ===============================
def run_app():
    if not st.session_state.get("api_key_valid", False):
        api_key_page()
    else:
        specs_page()

if __name__ == "__main__":
    run_app()
