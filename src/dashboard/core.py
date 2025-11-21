import streamlit as st
import sqlite3


@st.cache_resource
def get_connection():
    return sqlite3.connect("../../precon.db", check_same_thread=False)