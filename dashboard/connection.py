from sqlalchemy import create_engine
import streamlit as st


@st.cache_resource
def get_engine():
    DB_USER = "postgres"
    DB_PASSWORD = "123456"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "airport_revenue"

    database_url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    return create_engine(database_url)