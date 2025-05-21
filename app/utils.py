import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Load cleaned CSVs and add country label
    df_benin = pd.read_csv("data/benin_clean.csv", parse_dates=["Timestamp"])
    df_benin["country"] = "Benin"
    df_sl = pd.read_csv("data/sierraleone_clean.csv", parse_dates=["Timestamp"])
    df_sl["country"] = "Sierra Leone"
    df_togo = pd.read_csv("data/togo_clean.csv", parse_dates=["Timestamp"])
    df_togo["country"] = "Togo"

    # Concatenate into one DataFrame
    return pd.concat([df_benin, df_sl, df_togo], ignore_index=True)

def filter_data(df, countries, metric):
    # Subset for selected countries and metric
    return df[df["country"].isin(countries)][["Timestamp", "country", metric]]
