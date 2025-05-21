import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from utils import load_data, filter_data
from PIL import Image


# --- Page Config ---
im = Image.open("app/logo.ico")
st.set_page_config(
    page_title="Solar Data Dashboard",
    page_icon=im,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Title & Description ---
st.title(" :sun_with_face: Solar Irradiance Dashboard ")
st.markdown(
    """
    Explore solar metrics across Benin, Sierra Leone, and Togo.
    Use the controls on the left to filter by date, country, and metric.
    """
)

# --- Load Data ---
df = load_data()

# --- Sidebar Controls ---
st.sidebar.header("Filters")

# 1. Date Range
min_date, max_date = df["Timestamp"].min(), df["Timestamp"].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
start_date, end_date = map(lambda d: datetime.combine(d, datetime.min.time()), date_range)

# 2. Countries
countries = st.sidebar.multiselect(
    "Select Countries",
    options=df["country"].unique(),
    default=list(df["country"].unique())
)

# 3. Metric
metric = st.sidebar.selectbox(
    "Select Metric",
    options=["GHI", "DNI", "DHI"],
    index=0
)

# --- Filter Data ---
mask = (
        (df["country"].isin(countries)) &
        (df["Timestamp"] >= start_date) &
        (df["Timestamp"] <= end_date)
)
filtered = df.loc[mask, ["Timestamp", "country", metric, "RH"]]

# --- Main Dashboard Layout ---
col1, col2 = st.columns(2)

with col1:
    # Boxplot
    st.subheader(f"{metric} Comparison by Country")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.boxplot(
        x="country", y=metric,
        data=filtered,
        palette="Set2",
        ax=ax1
    )
    ax1.set_xlabel("Country")
    ax1.set_ylabel(metric)
    st.pyplot(fig1)

with col2:
    # Time-Series Trend
    st.subheader(f"{metric} Trend Over Time")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for country in countries:
        df_c = filtered[filtered["country"] == country]
        ts = df_c.set_index("Timestamp")[metric].resample("D").mean()
        ax2.plot(ts.index, ts.values, label=country)
    ax2.legend()
    ax2.set_xlabel("Date")
    ax2.set_ylabel(metric)
    st.pyplot(fig2)

st.markdown("---")

# --- Additional Visuals ---
col3, col4 = st.columns(2)

with col3:
    # Scatter: RH vs Metric
    st.subheader(f"RH vs. {metric}")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.scatterplot(
        x="RH", y=metric,
        hue="country",
        data=filtered.sample(min(2000, len(filtered)), random_state=42),
        palette="Set2",
        alpha=0.6,
        ax=ax3
    )
    ax3.set_xlabel("Relative Humidity (%)")
    ax3.set_ylabel(metric)
    st.pyplot(fig3)

with col4:
    # Bar Chart: Average metric by country
    st.subheader(f"Average {metric} by Country")
    avg_metric = (
        filtered
        .groupby("country")[metric]
        .mean()
        .sort_values(ascending=False)
    )
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    avg_metric.plot(kind="bar", ax=ax4)
    ax4.set_xlabel("Country")
    ax4.set_ylabel(f"Mean {metric} (W/m²)")
    ax4.set_xticklabels(avg_metric.index, rotation=0)
    st.pyplot(fig4)

st.markdown("---")

# --- Summary Table ---
st.subheader("Summary Statistics")
summary = (
    filtered
    .groupby("country")[metric]
    .agg(["mean", "median", "std"])
    .rename(columns={"mean": "Mean", "median": "Median", "std": "Std Dev"})
)
st.table(summary)