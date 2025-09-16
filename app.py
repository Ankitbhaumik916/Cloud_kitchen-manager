import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Cloud Kitchen Dashboard",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DB CONFIG ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "KAERMORHEN2311",
    "database": "cloud_kitchen"
}

# --- UTILITY FUNCTIONS ---
@st.cache_data(ttl=300)
def load_csv_data(csv_file=None, uploaded_file=None):
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success(f"✅ Uploaded file loaded: {uploaded_file.name}")
        elif csv_file and os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            st.sidebar.info(f"📁 Using local file: {csv_file}")
        else:
            st.sidebar.warning("⚠️ No CSV file found. Please upload a file or ensure 'order.csv' exists.")
            return pd.DataFrame()

        df.columns = df.columns.str.strip()
        if 'Order Placed At' in df.columns:
            df['Order Placed At'] = pd.to_datetime(df['Order Placed At'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        return pd.DataFrame()

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

@st.cache_data(ttl=300)
def load_mysql_data():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql("SELECT * FROM orders", conn)
        if 'Order Placed At' in df.columns:
            df['Order Placed At'] = pd.to_datetime(df['Order Placed At'], errors='coerce')
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error loading MySQL data: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
def main():
    st.title("🍴 Cloud Kitchen Orders Dashboard")
    
    with st.sidebar:
        st.header("⚙️ Settings")
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    csv_file = "order.csv"
    df_csv = load_csv_data(csv_file, uploaded_file)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📦 CSV Data", "🗄 MySQL Data", "🔄 Sync"])
    
    with tab1:
        st.header("Key Performance Indicators")
        df_mysql = load_mysql_data()
        
        if not df_mysql.empty:
            total_orders = len(df_mysql)
            total_sales = df_mysql["Total"].sum() if "Total" in df_mysql.columns else 0
            avg_rating = df_mysql["Rating"].mean() if "Rating" in df_mysql.columns else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Orders", f"{total_orders:,}")
            with col2:
                st.metric("Total Sales", f"₹{total_sales:,.2f}")
            with col3:
                st.metric("Avg Rating", f"{avg_rating:.2f}/5.0")
            with col4:
                completed_orders = len(df_mysql[df_mysql["Order Status"] == "Delivered"]) if "Order Status" in df_mysql.columns else 0
                completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            # --- New Charts ---
            st.subheader("📊 Sales Trends")
            col1, col2 = st.columns(2)

            with col1:
                if "Order Placed At" in df_mysql.columns and "Total" in df_mysql.columns:
                    daily_sales = df_mysql.groupby(df_mysql["Order Placed At"].dt.date)["Total"].sum().reset_index()
                    daily_sales.columns = ["Date", "Total Sales"]
                    fig_day = px.line(daily_sales, x="Date", y="Total Sales", markers=True, title="Sales vs Day")
                    st.plotly_chart(fig_day, use_container_width=True)

            with col2:
                if "Order Placed At" in df_mysql.columns and "Total" in df_mysql.columns:
                    df_mysql["Week"] = df_mysql["Order Placed At"].dt.to_period("W").astype(str)
                    weekly_sales = df_mysql.groupby("Week")["Total"].sum().reset_index()
                    weekly_sales.columns = ["Week", "Total Sales"]
                    fig_week = px.bar(weekly_sales, x="Week", y="Total Sales", text="Total Sales", title="Week-wise Sales Comparison")
                    fig_week.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                    st.plotly_chart(fig_week, use_container_width=True)

            # Existing Charts
            col3, col4 = st.columns(2)
            with col3:
                if "Order Status" in df_mysql.columns:
                    status_counts = df_mysql["Order Status"].value_counts()
                    fig_pie = px.pie(values=status_counts.values, names=status_counts.index, title="Order Status Distribution")
                    st.plotly_chart(fig_pie, use_container_width=True)
            with col4:
                if "Restaurant name" in df_mysql.columns and "Total" in df_mysql.columns:
                    top_restaurants = df_mysql.groupby("Restaurant name")["Total"].sum().sort_values(ascending=False).head(10)
                    fig_bar = px.bar(x=top_restaurants.values, y=top_restaurants.index, orientation='h', title="Top 10 Restaurants by Sales")
                    st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("📊 No data available for dashboard. Please sync CSV data first.")
    
    with tab2:
        st.header("📦 CSV Data Preview")
        if not df_csv.empty:
            st.info(f"📋 Total records in CSV: {len(df_csv)}")
            st.dataframe(df_csv, use_container_width=True, height=400)
        else:
            st.warning("⚠️ No CSV data found.")
    
    with tab3:
        st.header("🗄 MySQL Data Preview")
        df_mysql = load_mysql_data()
        if not df_mysql.empty:
            st.info(f"📋 Total records in MySQL: {len(df_mysql)}")
            st.dataframe(df_mysql, use_container_width=True, height=400)
        else:
            st.warning("⚠️ No MySQL data found.")
    
    with tab4:
        st.header("🔄 Data Synchronization")
        if not df_csv.empty:
            mysql_count = len(load_mysql_data())
            st.info(f"📊 MySQL Records: {mysql_count}")
            st.warning("⚠️ CSV sync feature is disabled in this version since you already created the table manually.")
        else:
            st.warning("⚠️ No CSV data to sync.")

if __name__ == "__main__":
    main()
