# Cloud Kitchen Orders Dashboard

## Overview

`Cloud Kitchen Orders Dashboard` is a Streamlit-based web application that allows cloud kitchen managers to monitor, analyze, and manage their orders efficiently. It supports CSV and MySQL data integration, visual analytics, AI-assisted insights, and real-time voice/text queries.

## Features

### Data Management

* **CSV Upload:** Upload daily or bulk order data in CSV format.
* **MySQL Sync:** Sync CSV data into a MySQL database with duplicate detection.
* **Clear Table:** Option to clear all data from the MySQL table.
* **Automatic Parsing:** Supports parsing order timestamps in multiple formats.

### Analytics Dashboard

* **Total Orders & Sales:** View total orders, sales, average ratings, and completion rates.
* **Daily Sales Trend:** Line chart showing sales over each day.
* **Weekly Sales Comparison:** Bar chart comparing weekly sales.
* **Top Restaurants:** Identify top 10 restaurants by sales.

### AI Assistant (Cloud Kitchen DSS)

* **Text & Voice Input:** Ask questions via text or speak your query.
* **Precomputed Summaries:** Generates business insights almost instantly.
* **Ollama Integration:** Uses `phi3:mini` or a custom trained model (`kitchen_ai`) for intelligent analytics.
* **Concise Recommendations:** Provides actionable insights based on the latest MySQL data.

### Technical Details

* **Frontend:** Streamlit web app
* **Backend Database:** MySQL (stores order data)
* **AI Integration:** Ollama `phi3:mini` / custom `kitchen_ai` model
* **Visualization:** Plotly Express for interactive charts
* **Voice Recognition:** SpeechRecognition library for microphone input

## Installation

1. Clone the repository:

   ```bash
   git clone <repo_url>
   cd cloud_kitchen_dashboard
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Ensure MySQL server is running and create a database, e.g., `cloud_kitchen`.

5. Update database credentials in `config.py` (or wherever `get_connection()` is defined).

## Running the App

```bash
streamlit run app2.py
```

* Upload your CSV file via sidebar.
* Use the tabs to view analytics, sync data, preview MySQL, or interact with the AI assistant.

## AI Assistant Setup

1. Ensure Ollama CLI is installed and the model is available:

   ```bash
   ollama list  # check available models
   ollama run phi3:mini  # test model
   ```

2. Optional: Train a custom model for the cloud kitchen manager (`kitchen_ai`).

3. The assistant uses precomputed summaries from MySQL for fast responses.

## CSV Format

The CSV file should have the following columns:

* Restaurant ID, Restaurant name, Subzone, City
* Order ID, Order Placed At (e.g., `07:04 PM, September 01 2025`)
* Order Status, Delivery, Distance, Items in order, Instructions
* Discounts, Bill subtotal, Packaging charges, Total, Rating, Review
* Cancellation/Reject reason, KPT duration, Rider wait time, Customer complaint tag, Customer ID

## Notes

* The app automatically converts order timestamps to MySQL-compatible datetime.
* Precomputed summaries are used in AI queries to reduce latency.
* Both voice and text queries are supported, but microphone access requires a local environment.

## Future Improvements

* Persistent AI session for almost instantaneous response.
* Enhanced DSS recommendations with predictive analytics.
* Multi-user support with role-based access.
* Real-time data updates via streaming or webhook integration.

Made by Ankit Bhaumik.
