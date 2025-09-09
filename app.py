import os, pandas as pd
import streamlit as st

st.set_page_config(page_title="OncoPrecio LATAM", layout="wide")
st.title("OncoPrecio LATAM – Alta especialidad")

USE_SUPABASE = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))

@st.cache_data(ttl=300)
def load_data():
    if USE_SUPABASE:
        from supabase import create_client
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        resp = supabase.table("prices").select("*").execute()
        df = pd.DataFrame(resp.data or [])
        if not df.empty and "last_seen_at" in df.columns:
            df["last_seen_at"] = pd.to_datetime(df["last_seen_at"])
        return df
    else:
        return pd.read_csv("prices_seed.csv")

df = load_data()
if df.empty:
    st.warning("Sin datos aún. Corre el ETL en Colab o configura Supabase.")
    st.stop()

col1, col2, col3 = st.columns(3)
countries = sorted(df["country"].dropna().unique().tolist())
drugs = sorted(df["drug_name"].dropna().unique().tolist())
sources = sorted(df["source_name"].dropna().unique().tolist())

with col1:
    f_country = st.multiselect("País", countries, default=countries)
with col2:
    f_drug = st.multiselect("Fármaco", drugs, default=drugs)
with col3:
    f_source = st.multiselect("Fuente", sources, default=sources)

f_df = df[
    df["country"].isin(f_country) &
    df["drug_name"].isin(f_drug) &
    df["source_name"].isin(f_source)
].copy()

st.caption(f"Resultados: {len(f_df)} filas")
st.dataframe(f_df.sort_values(["country","drug_name","price"]))

st.download_button("Descargar CSV", f_df.to_csv(index=False), file_name="oncoprecios.csv", mime="text/csv")
st.info("Precios informativos. Verificar presentación/fecha en la fuente original.")
