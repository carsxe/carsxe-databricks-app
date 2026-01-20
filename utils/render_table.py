import streamlit as st
import pandas as pd

def reformat(value):
    display_value = str(value)
    display_value = display_value.replace("_", " ")
    display_value = display_value.title()
    return display_value

def render_specs_table(data):
    rows = []
    nested = {}

    for k, v in data.items():
        if isinstance(v, dict) or isinstance(v, list):
            nested[k] = v
        else:
            rows.append({"Attribute": reformat(k), "Value": reformat(v)})

    if rows:
        df = pd.DataFrame(rows)
        st.table(df)

    for k, v in nested.items():
        with st.expander(reformat(k)):
            if isinstance(v, dict):
                render_specs_table(v)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        with st.expander(f"Item {i+1}"):
                            render_specs_table(item)
                    else:
                        st.write(reformat(item))
