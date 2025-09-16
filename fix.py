import pandas as pd

# Load CSV (comma separated)
df = pd.read_csv("order.csv")

# Clean column names (remove extra spaces/quotes)
df.columns = df.columns.str.strip().str.replace('"', '')

print("📦 Columns detected:")
print(df.columns.tolist())
print("\n📦 Data Preview:")
print(df.head(2))

# -----------------------------
# 1. Orders by Status
# -----------------------------
status_counts = df["Order Status"].value_counts()
print("\n📊 Orders by Status:")
print(status_counts)

# -----------------------------
# 2. Average Rating
# -----------------------------
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
avg_rating = df["Rating"].mean()
print(f"\n⭐ Average Rating: {avg_rating:.2f}")

# -----------------------------
# 3. Revenue after discounts
# -----------------------------
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
total_revenue = df["Total"].sum()
print(f"\n💰 Total Revenue: ₹{total_revenue:.2f}")

# -----------------------------
# 4. Performance metrics
# -----------------------------
df["KPT duration (minutes)"] = pd.to_numeric(df["KPT duration (minutes)"], errors="coerce")
df["Rider wait time (minutes)"] = pd.to_numeric(df["Rider wait time (minutes)"], errors="coerce")

avg_kpt = df["KPT duration (minutes)"].mean()
avg_wait = df["Rider wait time (minutes)"].mean()

print(f"\n⏱️ Avg Kitchen Prep Time: {avg_kpt:.2f} mins")
print(f"⏱️ Avg Rider Wait Time: {avg_wait:.2f} mins")

# -----------------------------
# 5. Save Summary
# -----------------------------
summary = {
    "Total Orders": len(df),
    "Delivered Orders": (df["Order Status"] == "Delivered").sum(),
    "Cancelled Orders": (df["Order Status"] == "Cancelled").sum(),
    "Total Revenue": total_revenue,
    "Avg Rating": avg_rating,
    "Avg KPT": avg_kpt,
    "Avg Rider Wait": avg_wait
}

pd.DataFrame([summary]).to_csv("orders_summary.csv", index=False)
print("\n✅ Summary saved to 'orders_summary.csv'")
