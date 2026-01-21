import streamlit as st
from prettytable import PrettyTable

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
            rows.append([reformat(k), str(v)])

    if rows:
        table = PrettyTable()
        table.field_names = ["Attribute", "Value"]
        table.align = "l"
        for row in rows:
            table.add_row(row)
        st.code(table.get_string(), language=None)

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
