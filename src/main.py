import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os
from export_excel import export_to_excel

def connect_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="skyanalytics_airways",
            user="postgres",
            password="0000"
        )
        print("✅ Connected to database successfully!")
        return conn
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def save_chart(fig, filename, description, rows):
    os.makedirs("charts", exist_ok=True)
    filepath = os.path.join("charts", filename)
    fig.savefig(filepath, bbox_inches="tight")
    plt.close(fig)
    print(f"📊 Saved {filename} | {rows} rows | {description}")

def create_charts(conn):
    q1 = """
        SELECT bc.check_result, COUNT(*) AS count
        FROM baggage_check bc
        JOIN baggage b ON bc.booking_id = b.booking_id
        GROUP BY bc.check_result;
    """
    df1 = pd.read_sql(q1, conn)
    fig1, ax1 = plt.subplots()
    df1.set_index("check_result")["count"].plot.pie(
        autopct='%1.1f%%', ax=ax1, ylabel=""
    )
    ax1.set_title("Baggage Check Results Distribution")
    save_chart(fig1, "pie_baggage_check.png", "Pie chart of baggage check results", len(df1))

    q2 = """
        SELECT airline_country, COUNT(*) AS airline_count
        FROM airline
        GROUP BY airline_country
        ORDER BY airline_count DESC
        LIMIT 10;
    """
    df2 = pd.read_sql(q2, conn)
    fig2, ax2 = plt.subplots()
    ax2.bar(df2["airline_country"], df2["airline_count"])
    ax2.set_title("Top 10 Countries by Airline Count")
    ax2.set_xlabel("Country")
    ax2.set_ylabel("Number of Airlines")
    save_chart(fig2, "bar_airlines_country.png", "Bar chart of airlines per country", len(df2))

    q3 = """
        SELECT bk.booking_platform, ROUND(AVG(b.weight_in_kg), 2) AS avg_weight
        FROM booking bk
        JOIN baggage b ON bk.booking_id = b.booking_id
        GROUP BY bk.booking_platform
        ORDER BY avg_weight DESC;
    """
    df3 = pd.read_sql(q3, conn)
    fig3, ax3 = plt.subplots()
    ax3.barh(df3["booking_platform"], df3["avg_weight"])
    ax3.set_title("Average Baggage Weight by Booking Platform")
    ax3.set_xlabel("Avg Weight (kg)")
    save_chart(fig3, "hbar_avg_baggage.png", "Horizontal bar: avg baggage weight by booking platform", len(df3))

    q4 = """
        SELECT DATE_TRUNC('month', created_date) AS month, COUNT(*) AS baggage_count
        FROM baggage
        GROUP BY month
        ORDER BY month;
    """
    df4 = pd.read_sql(q4, conn)
    fig4, ax4 = plt.subplots()
    ax4.plot(df4["month"], df4["baggage_count"], marker="o")
    ax4.set_title("Monthly Baggage Creation Trend")
    ax4.set_xlabel("Month")
    ax4.set_ylabel("Baggage Count")
    save_chart(fig4, "line_baggage_trend.png", "Line chart of baggage per month", len(df4))

    q5 = "SELECT weight_in_kg FROM baggage;"
    df5 = pd.read_sql(q5, conn)
    fig5, ax5 = plt.subplots()
    ax5.hist(df5["weight_in_kg"], bins=15, edgecolor="black")
    ax5.set_title("Baggage Weight Distribution")
    ax5.set_xlabel("Weight (kg)")
    ax5.set_ylabel("Frequency")
    save_chart(fig5, "hist_baggage_weight.png", "Histogram of baggage weights", len(df5))

    q6 = """
        SELECT b.weight_in_kg, bk.price
        FROM baggage b
        JOIN booking bk ON b.booking_id = bk.booking_id
        WHERE bk.price IS NOT NULL
        LIMIT 500;
    """
    df6 = pd.read_sql(q6, conn)
    fig6, ax6 = plt.subplots()
    ax6.scatter(df6["price"], df6["weight_in_kg"], alpha=0.5)
    ax6.set_title("Baggage Weight vs Booking Price")
    ax6.set_xlabel("Booking Price")
    ax6.set_ylabel("Weight (kg)")
    save_chart(fig6, "scatter_baggage_price.png", "Scatter: baggage weight vs booking price", len(df6))

def display_summary(conn):
    print("\n" + "="*50)
    print("DATABASE SUMMARY")
    print("="*50)
    tables = ['airline', 'airport', 'baggage', 'baggage_check', 'boarding_pass', 'booking']
    for t in tables:
        df = pd.read_sql(f"SELECT COUNT(*) AS count FROM {t}", conn)
        print(f"{t:<15}: {df['count'][0]} rows")

def main():
    conn = connect_db()
    if not conn:
        return
    try:
        create_charts(conn)
        df_airlines = pd.read_sql("SELECT * FROM airline LIMIT 20;", conn)
        df_baggage = pd.read_sql("SELECT * FROM baggage LIMIT 20;", conn)

        export_to_excel(
            {
                "Airlines": df_airlines,
                "Baggage": df_baggage
            },
            "report.xlsx"
        )
        display_summary(conn)

        print("\nAssignment 2 completed: Charts + Plotly + Excel Export")

    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
