import plotly.express as px
import pandas as pd
import psycopg2
import os

def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="skyanalytics_airways",
        user="postgres",
        password="0000"
    )

def plotly_time_slider(conn):
    q = """
        SELECT DATE_TRUNC('month', created_date) AS month,
               COUNT(*) AS baggage_count
        FROM baggage
        GROUP BY month
        ORDER BY month;
    """
    df = pd.read_sql(q, conn)

    df["month"] = pd.to_datetime(df["month"], utc=True)
    
    fig = px.line(
        df,
        x="month",
        y="baggage_count",
        title="Baggage Creation Trend Over Time",
        markers=True
    )

    fig.update_xaxes(rangeslider_visible=True)

    os.makedirs("charts", exist_ok=True)
    filepath = os.path.join("charts", "plotly_baggage_slider.html")
    fig.write_html(filepath)

    print(f"Saved interactive Plotly chart with time slider → {filepath}")

def main():
    conn = connect_db()
    try:
        plotly_time_slider(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
