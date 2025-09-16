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

# --- DB CONNECTION ---
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# --- LOAD FUNCTIONS ---
def load_csv_data(uploaded_file=None, csv_file=None):
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success(f"✅ Uploaded file loaded: {uploaded_file.name}")
        elif csv_file and os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            st.sidebar.info(f"📁 Using local file: {csv_file}")
        else:
            return pd.DataFrame()

        df.columns = df.columns.str.strip()
        if "Order Placed At" in df.columns:
            df["Order Placed At"] = pd.to_datetime(df["Order Placed At"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        return pd.DataFrame()

def load_mysql_data():
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql("SELECT * FROM orders", conn)
        if "Order Placed At" in df.columns:
            df["Order Placed At"] = pd.to_datetime(df["Order Placed At"], errors="coerce")
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error loading MySQL data: {e}")
        return pd.DataFrame()

# --- INSERT FUNCTION ---
def sync_to_mysql(df):
    if df.empty:
        return 0, 0

    inserted, skipped = 0, 0
    try:
        conn = get_connection()
        if conn is None:
            return 0, 0
        cursor = conn.cursor()

        # Convert 'Order Placed At' to proper MySQL datetime
        if "Order Placed At" in df.columns:
            df["Order Placed At"] = pd.to_datetime(
                df["Order Placed At"], 
                format="%I:%M %p, %B %d %Y",  # matches CSV format
                errors="coerce"
            ).dt.strftime("%Y-%m-%d %H:%M:%S")

        insert_query = """
        INSERT IGNORE INTO orders
        (`Restaurant ID`, `Restaurant name`, `Subzone`, `City`, `Order ID`, `Order Placed At`,
         `Order Status`, `Delivery`, `Distance`, `Items in order`, `Instructions`, `Discount construct`,
         `Bill subtotal`, `Packaging charges`, `Restaurant discount (Promo)`,
         `Restaurant discount (Flat offs, Freebies & others)`, `Gold discount`, `Brand pack discount`,
         `Total`, `Rating`, `Review`, `Cancellation / Rejection reason`,
         `Restaurant compensation (Cancellation)`, `Restaurant penalty (Rejection)`,
         `KPT duration (minutes)`, `Rider wait time (minutes)`, `Order Ready Marked`,
         `Customer complaint tag`, `Customer ID`)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        # Prepare values
        values = []
        for _, row in df.iterrows():
            # ensure NaN stays None for MySQL
            row_values = tuple(
                None if pd.isna(row.get(col)) else row.get(col) for col in [
                    "Restaurant ID","Restaurant name","Subzone","City","Order ID","Order Placed At",
                    "Order Status","Delivery","Distance","Items in order","Instructions","Discount construct",
                    "Bill subtotal","Packaging charges","Restaurant discount (Promo)",
                    "Restaurant discount (Flat offs, Freebies & others)","Gold discount","Brand pack discount",
                    "Total","Rating","Review","Cancellation / Rejection reason",
                    "Restaurant compensation (Cancellation)","Restaurant penalty (Rejection)",
                    "KPT duration (minutes)","Rider wait time (minutes)","Order Ready Marked",
                    "Customer complaint tag","Customer ID"
                ]
            )
            values.append(row_values)

        cursor.executemany(insert_query, values)
        conn.commit()

        # Count inserted vs skipped
        inserted = cursor.rowcount
        skipped = len(df) - inserted

        cursor.close()
        conn.close()

    except Exception as e:
        st.error(f"❌ Sync error: {e}")

    return inserted, skipped


def main():
    st.title("🍴 Cloud Kitchen Orders Dashboard")

    with st.sidebar:
        st.header("⚙️ Settings")
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        csv_file = "order.csv"

    # --- Load CSV ---
    df_csv = load_csv_data(csv_file=csv_file, uploaded_file=uploaded_file)

    # --- Convert Order Placed At from CSV formats to datetime (robust) ---
    if not df_csv.empty and "Order Placed At" in df_csv.columns:
        # Try to parse commonly found format like "07:04 PM, September 01 2025"
        def try_parse_order_placed(val):
            if pd.isna(val):
                return pd.NaT
            if isinstance(val, (pd.Timestamp, datetime)):
                return pd.to_datetime(val)
            s = str(val).strip()
            # Try the custom format first
            for fmt in ("%I:%M %p, %B %d %Y", "%I:%M %p, %B %d, %Y", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S"):
                try:
                    return pd.to_datetime(s, format=fmt)
                except Exception:
                    pass
            # fallback to pandas parser
            try:
                return pd.to_datetime(s, errors='coerce')
            except Exception:
                return pd.NaT

        df_csv["Order Placed At"] = df_csv["Order Placed At"].apply(try_parse_order_placed)

    # --- Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Dashboard", "📦 CSV Data", "🗄 MySQL Data", "🔄 Sync", "🤖 AI Assistant"]
    )

    # --- Analytics Dashboard ---
    with tab1:
        st.header("📊 Analytics Dashboard")

        # Always reload MySQL data fresh
        df_mysql = load_mysql_data()

        if not df_mysql.empty:
            # Ensure correct datetime dtype for MySQL 'Order Placed At'
            if "Order Placed At" in df_mysql.columns:
                df_mysql["Order Placed At"] = pd.to_datetime(df_mysql["Order Placed At"], errors="coerce")

            total_orders = len(df_mysql)
            total_sales = df_mysql["Total"].sum() if "Total" in df_mysql.columns else 0
            avg_rating = df_mysql["Rating"].mean() if "Rating" in df_mysql.columns else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Orders", f"{total_orders:,}")
            col2.metric("Total Sales", f"₹{total_sales:,.2f}")
            col3.metric("Avg Rating", f"{avg_rating:.2f}/5.0")
            completed_orders = (
                len(df_mysql[df_mysql["Order Status"] == "Delivered"])
                if "Order Status" in df_mysql.columns
                else 0
            )
            completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
            col4.metric("Completion Rate", f"{completion_rate:.1f}%")

            st.markdown("---")

            # --- Daily Sales (Day-on-Day) ---
            if "Order Placed At" in df_mysql.columns and "Total" in df_mysql.columns:
                daily_sales = (
                    df_mysql.groupby(df_mysql["Order Placed At"].dt.date)["Total"]
                    .sum()
                    .reset_index()
                )
                daily_sales.columns = ["Date", "Total Sales"]
                fig_day = px.line(daily_sales, x="Date", y="Total Sales", title="Sales vs Day", markers=True)
                st.plotly_chart(fig_day, use_container_width=True)

            # --- Week-wise Sales ---
            if "Order Placed At" in df_mysql.columns and "Total" in df_mysql.columns:
                df_mysql["Week"] = df_mysql["Order Placed At"].dt.to_period("W").astype(str)
                weekly_sales = df_mysql.groupby("Week")["Total"].sum().reset_index()
                weekly_sales.columns = ["Week", "Total Sales"]
                fig_week = px.bar(
                    weekly_sales,
                    x="Week",
                    y="Total Sales",
                    text="Total Sales",
                    title="Weekly Sales Comparison",
                )
                fig_week.update_traces(texttemplate="%{text:.2s}", textposition="outside")
                st.plotly_chart(fig_week, use_container_width=True)

            st.markdown("---")

            # --- Top Restaurants ---
            if "Restaurant name" in df_mysql.columns and "Total" in df_mysql.columns:
                top_restaurants = (
                    df_mysql.groupby("Restaurant name")["Total"].sum().sort_values(ascending=False).head(10)
                )
                fig_top = px.bar(
                    x=top_restaurants.values,
                    y=top_restaurants.index,
                    orientation="h",
                    title="Top 10 Restaurants by Sales",
                )
                st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("📊 No MySQL data found. Please sync first.")

    # --- CSV Data Preview ---
    with tab2:
        st.header("📦 CSV Data Preview")
        if not df_csv.empty:
            # show small sample and allow download
            st.dataframe(df_csv, use_container_width=True, height=400)
            csv_download = df_csv.to_csv(index=False)
            st.download_button("📥 Download CSV", csv_download, "orders_preview.csv", "text/csv")
        else:
            st.warning("⚠️ No CSV data uploaded")

    # --- MySQL Data Preview ---
    with tab3:
        st.header("🗄 MySQL Data Preview")
        df_mysql = load_mysql_data()  # reload
        if not df_mysql.empty:
            st.dataframe(df_mysql, use_container_width=True, height=400)
        else:
            st.warning("⚠️ No data in MySQL")

    # --- Sync CSV → MySQL ---
    with tab4:
        st.header("🔄 Data Sync")

        if not df_csv.empty:
            col1, col2 = st.columns([2, 1])

            with col1:
                if st.button("⬆️ Sync to MySQL"):
                    with st.spinner("Syncing CSV to MySQL..."):
                        # Call your sync function (make sure it handles datetimes and IGNORE duplicates)
                        inserted, skipped = sync_to_mysql(df_csv)
                        st.success(f"✅ Sync complete! Inserted: {inserted}, Skipped (duplicates): {skipped}")

                        # Refresh and show updated MySQL table
                        df_mysql = load_mysql_data()
                        st.subheader("📊 Updated MySQL Table")
                        if not df_mysql.empty:
                            st.dataframe(df_mysql, use_container_width=True, height=400)
                        else:
                            st.info("No data after sync (unexpected).")

            with col2:
                # Clear table with confirmation
                if st.button("🧹 Clear MySQL Table"):
                    if st.checkbox("I confirm: delete ALL rows from MySQL orders table"):
                        try:
                            conn = get_connection()
                            if conn:
                                cur = conn.cursor()
                                cur.execute("DELETE FROM orders")
                                conn.commit()
                                cur.close()
                                conn.close()
                                st.warning("⚠️ All data cleared from MySQL table!")
                                # reload to reflect changes
                                df_mysql = load_mysql_data()
                        except Exception as e:
                            st.error(f"❌ Error clearing table: {e}")
        else:
            st.warning("⚠️ No CSV data available to sync.")

    # --- AI Assistant ---
    import pyttsx3
    import speech_recognition as sr
    import subprocess

    # -----------------------------
    # Initialize persistent model & TTS
    # -----------------------------
    if 'ai_model_loaded' not in st.session_state:
        st.session_state['ai_model_loaded'] = True
        # This is a dummy persistent placeholder; replace with your actual Ollama API or Python SDK call
        st.session_state['model_name'] = "phi3:mini"

    if 'summary' not in st.session_state:
        df_mysql = load_mysql_data()
        if not df_mysql.empty:
            total_orders = len(df_mysql)
            total_sales = df_mysql["Total"].sum() if "Total" in df_mysql.columns else 0
            avg_rating = df_mysql["Rating"].mean() if "Rating" in df_mysql.columns else 0
            context_lines = [
                f"Total Orders: {total_orders}",
                f"Total Sales: {total_sales:.2f}",
                f"Average Rating: {avg_rating:.2f}/5.0"
            ]
            if "Restaurant name" in df_mysql.columns and "Total" in df_mysql.columns:
                top5 = (
                    df_mysql.groupby("Restaurant name")["Total"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(5)
                )
                context_lines.append("Top restaurants (by sales):")
                for r, s in zip(top5.index, top5.values):
                    context_lines.append(f"- {r}: {s:.0f}")
            st.session_state['summary'] = "\n".join(context_lines)
        else:
            st.session_state['summary'] = "No MySQL data available."

    # -----------------------------
    # Initialize TTS engine once
    # -----------------------------
    if 'tts_engine' not in st.session_state:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        st.session_state['tts_engine'] = engine

    def speak(text):
        """Speak text using pyttsx3"""
        engine = st.session_state['tts_engine']
        engine.say(text)
        engine.runAndWait()
# --- Load AI model once ---
   # --- Load AI session once ---
    if "ai_session" not in st.session_state:
        with st.spinner("Loading kitchen_ai..."):
            try:
                import subprocess
                # NOTE: This will keep the model in memory
                st.session_state["ai_session"] = "kitchen_ai"  # placeholder for persistent session
                st.success("✅ kitchen_ai loaded and ready!")
            except Exception as e:
                st.error(f"⚠️ Failed to load AI: {e}")

    # --- AI Assistant Tab ---
    with tab5:
        st.header("🤖 AI Assistant")
        input_mode = st.radio("Input Mode:", ["Text", "Voice"], horizontal=True)

        user_query = ""
        ask_button = False

        if input_mode == "Text":
            user_query = st.text_area("Ask anything about your Cloud Kitchen data:")
            ask_button = st.button("🚀 Ask Assistant")
        else:
            if st.button("🎤 Speak Your Question"):
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    st.info("Listening...")
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        user_query = recognizer.recognize_google(audio)
                        st.success(f"You said: {user_query}")
                        ask_button = True
                    except Exception as e:
                        st.error(f"⚠️ Speech Recognition error: {e}")

        if ask_button and user_query.strip():
            with st.spinner("Thinking... 🤔"):
                # Build prompt from precomputed summary
                prompt = f"{st.session_state.get('summary', '')}\n\nUser Question: {user_query}"

                try:
                    # Use persistent kitchen_ai session (low latency)
                    proc = subprocess.run(
                        ["ollama", "run", "kitchen_ai"],
                        input=prompt,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        encoding="utf-8"
                    )
                    response = proc.stdout.strip() if proc.returncode == 0 else proc.stderr.strip()
                except subprocess.TimeoutExpired:
                    response = "⚠️ AI request timed out."
                except Exception as e:
                    response = f"⚠️ Error calling AI: {e}"

                st.subheader("💡 Assistant’s Response")
                st.write(response)



if __name__ == "__main__":
    main()
