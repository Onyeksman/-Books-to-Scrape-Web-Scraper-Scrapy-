# app.py
# Client-ready interactive Streamlit dashboard for Books to Scrape data
# Assumes the Scrapy spider wrote a CSV file named "books_info.csv" in the same folder.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO
from urllib.parse import urljoin

st.set_page_config(page_title="Books Dashboard", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_and_clean(path: str = "books_info.csv") -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")

    # Normalize column names (in case of minor differences)
    df.columns = [c.strip() for c in df.columns]

    # Ensure columns exist
    for col in ["Book Title", "Book Price", "Instock Availability", "Rating", "Image URL"]:
        if col not in df.columns:
            df[col] = ""

    # Clean price: remove currency symbols and artifacts and convert to float
    def parse_price(p):
        if pd.isna(p):
            return np.nan
        s = str(p).replace("Â", "").strip()
        # remove any non-digit, non-dot, non-comma
        s = s.replace("£", "").replace("$", "").replace(",", "")
        try:
            return float(s)
        except Exception:
            # fallback: extract digits
            import re
            m = re.search(r"\d+(?:\.\d+)?", s)
            return float(m.group(0)) if m else np.nan

    df["price"] = df["Book Price"].apply(parse_price)

    # Clean availability
    df["availability"] = df["Instock Availability"].fillna("").apply(lambda x: str(x).strip())

    # Normalize rating: convert words to integer where possible
    # Books to Scrape uses words in the class (One, Two, Three, Four, Five)
    word_to_num = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    def parse_rating(r):
        if pd.isna(r):
            return np.nan
        s = str(r).strip()
        # sometimes rating may come as 'star-rating Three' or just 'Three'
        for k, v in word_to_num.items():
            if k.lower() in s.lower():
                return v
        # try to parse digits
        import re
        m = re.search(r"(\d+)", s)
        return int(m.group(1)) if m else np.nan

    df["rating_num"] = df["Rating"].apply(parse_rating)

    # Fix image urls — many are relative in books.toscrape dataset
    def fix_image_url(u):
        u = str(u)
        if not u:
            return ""
        u = u.strip()
        if u.startswith("http"):
            return u
        # assume common site root
        return urljoin("https://books.toscrape.com/", u)

    df["image_url_fixed"] = df["Image URL"].fillna("").apply(fix_image_url)

    # Add a short title for UI where titles are long
    df["title_short"] = df["Book Title"].astype(str).apply(lambda x: x if len(x) <= 60 else x[:57] + "...")

    return df


# ---------- UI: Sidebar filters ----------
st.title("📚 Books Dashboard")
st.markdown("Interactive dashboard for book pricing, ratings and availability (data from `books_info.csv`).")

with st.sidebar:
    st.header("Filters")
    data_file = st.file_uploader("Upload CSV (optional)", type=["csv"], help="If left empty, will load './books_info.csv'.")
    use_sample = st.checkbox("Use packaged CSV (books_info.csv)", value=True)

    min_price = st.number_input("Min price", value=0.0, step=0.5)
    max_price = st.number_input("Max price", value=100.0, step=0.5)

    rating_options = st.multiselect("Ratings", options=[1,2,3,4,5], default=[1,2,3,4,5])
    availability_filter = st.selectbox("Availability", options=["All","In stock","Out of stock"], index=0)
    title_search = st.text_input("Search title", value="", help="Search by partial book title")
    show_images = st.checkbox("Show images", value=True)
    show_table = st.checkbox("Show data table", value=True)

    st.markdown("---")
    st.markdown("**Export**")
    st.write("After filtering you can export the filtered dataset from the main page.")

# ---------- Load data ----------
try:
    if data_file is not None:
        # read uploaded file
        df_raw = pd.read_csv(data_file)
    else:
        df_raw = load_and_clean("books_info.csv") if use_sample else load_and_clean("books_info.csv")
except FileNotFoundError:
    st.error("Could not find 'books_info.csv' in the current directory. Upload a CSV in the sidebar or place the CSV next to this app.")
    st.stop()

# If user uploaded, still run cleaning steps
if data_file is not None:
    # use same cleaning pipeline but with temp csv
    df_raw = load_and_clean(path=data_file)

# ---------- Apply filters ----------
df = df_raw.copy()

# Price bounds: if there are NaNs, fill with 0 for bounding behavior
price_min_val = float(np.nanmin(df["price"])) if df["price"].notna().any() else 0.0
price_max_val = float(np.nanmax(df["price"])) if df["price"].notna().any() else 100.0

# If default sidebar bounds are same as placeholder, set to entire range
if min_price == 0.0 and max_price == 100.0:
    min_price = price_min_val
    max_price = price_max_val

# Apply numeric filter
df = df[(df["price"].fillna(-1) >= min_price) & (df["price"].fillna(999999) <= max_price)]

# Rating filter
df = df[df["rating_num"].isin(rating_options)]

# Availability filter
if availability_filter == "In stock":
    df = df[df["availability"].str.lower().str.contains("in stock") | df["availability"].str.lower().str.contains("available")]
elif availability_filter == "Out of stock":
    df = df[~(df["availability"].str.lower().str.contains("in stock") | df["availability"].str.lower().str.contains("available"))]

# Title search
if title_search:
    df = df[df["Book Title"].str.contains(title_search, case=False, na=False)]

# ---------- Top-level metrics ----------
col1, col2, col3, col4 = st.columns([2,2,2,2])
with col1:
    st.metric("Books (filtered)", value=len(df))
with col2:
    avg_price = df["price"].mean() if len(df) else 0
    st.metric("Avg price", value=f"{avg_price:.2f}")
with col3:
    avg_rating = df["rating_num"].mean() if len(df) else 0
    st.metric("Avg rating", value=f"{avg_rating:.2f}")
with col4:
    in_stock_count = df[df["availability"].str.lower().str.contains("in stock")].shape[0]
    st.metric("In stock", value=in_stock_count)

st.markdown("---")

# ---------- Charts ----------
chart_col1, chart_col2 = st.columns([3,2])

with chart_col1:
    st.subheader("Price distribution")
    if df["price"].notna().any():
        fig = px.histogram(df, x="price", nbins=30, marginal="box", title="Price distribution")
        fig.update_layout(xaxis_title="Price", yaxis_title="Count", bargap=0.02)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No price data available to show histogram.")

with chart_col2:
    st.subheader("Ratings breakdown")
    ratings_count = df["rating_num"].value_counts().reindex([1,2,3,4,5]).fillna(0).astype(int)
    r_df = pd.DataFrame({"rating": ratings_count.index, "count": ratings_count.values})
    fig2 = px.bar(r_df, x="rating", y="count", labels={"rating":"Rating","count":"Count"}, title="Ratings")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ---------- Data Table & Images ----------
if show_table:
    st.subheader("Filtered data")
    display_cols = [c for c in ["Book Title", "price", "rating_num", "availability", "image_url_fixed"] if c in df.columns]
    df_display = df[display_cols].rename(columns={"price":"Price", "rating_num":"Rating", "image_url_fixed":"Image URL"})
    st.dataframe(df_display.reset_index(drop=True))

# Image gallery (first N items)
if show_images:
    max_show = st.number_input("Max images to show", min_value=4, max_value=60, value=12, step=4)
    st.subheader("Book covers")
    to_show = df.head(max_show)
    cols = st.columns(4)
    for i, (_, row) in enumerate(to_show.iterrows()):
        c = cols[i % 4]
        with c:
            if row.get("image_url_fixed"):
                try:
                    st.image(row["image_url_fixed"], width=140, caption=row["title_short"])
                except Exception:
                    st.write(row["title_short"])
            else:
                st.write(row["title_short"])

st.markdown("---")

# ---------- Export filtered CSV ----------
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)
csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")

st.download_button("Download filtered CSV", data=csv_bytes, file_name="books_filtered.csv", mime="text/csv")

# ---------- Footer / Help ----------
st.markdown("---")
st.write("**Notes:** This dashboard exports the CSV generated by the provided Scrapy spider. If your CSV has different column names, rename them or upload the CSV in the sidebar.")
st.write("If you'd like, I can adapt the layout, add additional visualizations (time-series if you collect over time), or prepare a deployable container (Docker + Streamlit).")

