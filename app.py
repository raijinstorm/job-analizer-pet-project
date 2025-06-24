import os
import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime

# ────────────────────────────────────────────────
# 1. CONNECTION & CACHING
# ────────────────────────────────────────────────
@st.cache_data(ttl=600)  # auto-refresh every 10 min
def load_data() -> pd.DataFrame:
    load_dotenv()
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
        f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
    )
    df = pd.read_sql("SELECT * FROM postings", engine)
    df['publication_date'] = pd.to_datetime(df['publication_date'])
    return df

df = load_data()

# ────────────────────────────────────────────────
# 2. SIDEBAR  FILTERS
# ────────────────────────────────────────────────
st.sidebar.header("🔍 Filter jobs")
keyword = st.sidebar.text_input("Keyword in title/company", "")
date_min, date_max = st.sidebar.date_input(
    "Publication date range",
    [df['publication_date'].min(), df['publication_date'].max()],
)
company_sel = st.sidebar.multiselect(
    "Company", options=sorted(df['company_name'].unique()), default=[]
)
job_type_sel = st.sidebar.multiselect(
    "Job type", options=sorted(df['job_type'].unique()), default=[]
)

mask = (
    df['title'].str.contains(keyword, case=False, na=False)
    | df['company_name'].str.contains(keyword, case=False, na=False)
) if keyword else True
mask &= df['publication_date'].between(pd.to_datetime(date_min), pd.to_datetime(date_max))
if company_sel:
    mask &= df['company_name'].isin(company_sel)
if job_type_sel:
    mask &= df['job_type'].isin(job_type_sel)

df_filt = df.loc[mask]

# ────────────────────────────────────────────────
# 3. KPI CARDS
# ────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("🗂️ Total postings",      f"{len(df_filt):,}")
col2.metric("🏢 Unique companies",    df_filt['company_name'].nunique())
col3.metric("🕒 Newest posting",      df_filt['publication_date'].max().strftime("%Y-%m-%d"))

st.markdown("---")

# ────────────────────────────────────────────────
# 4. CHARTS
# ────────────────────────────────────────────────
st.subheader("Job type distribution")
chart_jobtype = (
    alt.Chart(df_filt)
    .mark_bar()
    .encode(
        y=alt.Y('job_type:N', sort='-x', title=''),
        x=alt.X('count():Q', title='Count'),
        tooltip=['job_type', alt.Tooltip('count()', title='Count')]
    )
    .properties(height=250)
)
st.altair_chart(chart_jobtype, use_container_width=True)

st.subheader("Daily postings trend")
daily = df_filt.groupby(df_filt['publication_date'].dt.date).size().reset_index(name='cnt')
chart_daily = (
    alt.Chart(daily)
    .mark_line(point=True)
    .encode(
        x=alt.X('publication_date:T', title='Date'),
        y=alt.Y('cnt:Q', title='Postings'),
        tooltip=['publication_date', 'cnt']
    )
    .properties(height=250)
)
st.altair_chart(chart_daily, use_container_width=True)

# Optional pie by company
# after filters and df_filt defined...
raw_top = df_filt['company_name'].value_counts().head(10).reset_index()
# st.write("Before rename:", raw_top.columns.tolist(), raw_top.dtypes)

# 2. Rename columns properly
cols = raw_top.columns.tolist()
if cols == ['index', 'company_name']:
    top_companies = raw_top.rename(columns={'index': 'company', 'company_name': 'cnt'})
elif cols == ['index', 'count']:
    top_companies = raw_top.rename(columns={'index': 'company', 'count': 'cnt'})
else:
    top_companies = raw_top.copy()
    top_companies.columns = ['company', 'cnt']
# st.write("After rename:", top_companies.columns.tolist(), top_companies.dtypes)

# 3. Plot
st.subheader("Top 10 companies")
if top_companies.empty:
    st.warning("No company data to display.")
else:
    chart_company = (
        alt.Chart(top_companies)
        .mark_arc()
        .encode(
            theta=alt.Theta('cnt:Q', title='Count'),
            color=alt.Color('company:N', title='Company'),
            tooltip=[alt.Tooltip('company:N', title='Company'),
                     alt.Tooltip('cnt:Q', title='Count')]
        )
        .properties(height=350)
    )
    st.altair_chart(chart_company, use_container_width=True)


st.markdown("---")

# ────────────────────────────────────────────────
# 5. RAW TABLE + DOWNLOAD
# ────────────────────────────────────────────────
st.subheader("Raw data")
st.dataframe(df_filt, use_container_width=True, hide_index=True)

csv = df_filt.to_csv(index=False).encode()
st.download_button(
    label="📥 Download current view (CSV)",
    data=csv,
    file_name=f"postings_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime='text/csv',
)

# ────────────────────────────────────────────────
# 6. FOOTER
# ────────────────────────────────────────────────
st.caption(f"Data last refreshed {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
