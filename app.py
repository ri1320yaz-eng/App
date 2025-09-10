import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime

# Set page config

st.set_page_config(
page_title=“Portfolio Tracker”,
page_icon=“📈”,
layout=“centered”
)

# App title

st.title(“📈 My Portfolio Tracker”)
st.markdown(“Real-time returns for your stock portfolio”)

# Stock data

STOCK_DATA = {
“DIXON”: {“url”: “https://www.screener.in/company/DIXON/consolidated/”, “allocation”: 10.08},
“COFORGE”: {“url”: “https://www.screener.in/company/COFORGE/consolidated/”, “allocation”: 9.79},
“TRENT”: {“url”: “https://www.screener.in/company/TRENT/consolidated/”, “allocation”: 9.14},
“ETERNAL”: {“url”: “https://www.screener.in/company/ETERNAL/consolidated/”, “allocation”: 9.03},
“KALYANKJIL”: {“url”: “https://www.screener.in/company/KALYANKJIL/consolidated/”, “allocation”: 8.70},
“PAYTM”: {“url”: “https://www.screener.in/company/PAYTM/consolidated/”, “allocation”: 8.68},
“PERSISTENT”: {“url”: “https://www.screener.in/company/PERSISTENT/consolidated/”, “allocation”: 8.39},
“POLYCAB”: {“url”: “https://www.screener.in/company/POLYCAB/consolidated/”, “allocation”: 6.22},
“KEI”: {“url”: “https://www.screener.in/company/KEI/”, “allocation”: 4.11},
“KAYNES”: {“url”: “https://www.screener.in/company/KAYNES/consolidated/”, “allocation”: 3.70},
“BHARTIHEXA”: {“url”: “https://www.screener.in/company/BHARTIHEXA/”, “allocation”: 3.34},
“MAXHEALTH”: {“url”: “https://www.screener.in/company/MAXHEALTH/consolidated/”, “allocation”: 3.21},
“ABCAPITAL”: {“url”: “https://www.screener.in/company/ABCAPITAL/consolidated/”, “allocation”: 3.20},
“TIINDIA”: {“url”: “https://www.screener.in/company/TIINDIA/consolidated/”, “allocation”: 2.98},
“PRESTIGE”: {“url”: “https://www.screener.in/company/PRESTIGE/consolidated/”, “allocation”: 2.58},
“SUPREMEIND”: {“url”: “https://www.screener.in/company/SUPREMEIND/consolidated/”, “allocation”: 2.38},
“KPITTECH”: {“url”: “https://www.screener.in/company/KPITTECH/consolidated/”, “allocation”: 1.03},
“POWERINDIA”: {“url”: “https://www.screener.in/company/POWERINDIA”, “allocation”: 0.86}
}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_return(url, stock_name):
“”“Fetch stock return from screener.in”””
try:
headers = {
‘User-Agent’: ‘Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36’
}
response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()
soup = BeautifulSoup(response.text, “html.parser”)

```
    # Use regex to find the first occurrence of a percentage value
    match = re.search(r"[+-]?[0-9]+\.[0-9]+(?=%)", soup.text)
    if match:
        return float(match.group())
    else:
        return 0.0
except Exception as e:
    st.error(f"Error fetching data for {stock_name}: {str(e)}")
    return 0.0
```

def calculate_portfolio_return():
“”“Calculate weighted portfolio return”””
portfolio_data = []
total_allocation = sum(data[“allocation”] for data in STOCK_DATA.values())

```
# Progress bar
progress_bar = st.progress(0)
status_text = st.empty()

total_weighted_return = 0

for i, (stock_name, data) in enumerate(STOCK_DATA.items()):
    status_text.text(f'Fetching data for {stock_name}...')
    
    stock_return = fetch_stock_return(data["url"], stock_name)
    normalized_allocation = data["allocation"] / total_allocation
    weighted_return = stock_return * normalized_allocation
    total_weighted_return += weighted_return
    
    portfolio_data.append({
        "Stock": stock_name,
        "Return (%)": f"{stock_return:+.2f}%",
        "Allocation (%)": f"{data['allocation']:.2f}%",
        "Weighted Return (%)": f"{weighted_return:+.4f}%"
    })
    
    # Update progress
    progress_bar.progress((i + 1) / len(STOCK_DATA))
    time.sleep(0.1)  # Small delay to avoid overwhelming the server

progress_bar.empty()
status_text.empty()

return portfolio_data, total_weighted_return
```

# Main app

def main():
# Add refresh button
if st.button(“🔄 Refresh Data”, type=“primary”):
st.cache_data.clear()
st.rerun()

```
st.markdown("---")

# Show last updated time
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with st.spinner("Fetching portfolio data..."):
    portfolio_data, total_return = calculate_portfolio_return()

# Display overall portfolio return
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Portfolio Return Today",
        value=f"{total_return:+.2f}%",
        delta=None
    )

with col2:
    positive_stocks = len([stock for stock in portfolio_data if float(stock["Return (%)"].replace('%', '').replace('+', '')) > 0])
    st.metric(
        label="Stocks in Green",
        value=f"{positive_stocks}/{len(portfolio_data)}"
    )

with col3:
    total_allocation = sum(float(stock["Allocation (%)"].replace('%', '')) for stock in portfolio_data)
    st.metric(
        label="Total Allocation",
        value=f"{total_allocation:.1f}%"
    )

st.markdown("---")

# Display individual stocks
st.subheader("📊 Individual Stock Performance")

# Create DataFrame
df = pd.DataFrame(portfolio_data)

# Style the dataframe
def highlight_returns(val):
    if isinstance(val, str) and '%' in val and ('Return' in val or 'Weighted' in val):
        numeric_val = float(val.replace('%', '').replace('+', ''))
        if numeric_val > 0:
            return 'background-color: #d4edda; color: #155724'
        elif numeric_val < 0:
            return 'background-color: #f8d7da; color: #721c24'
    return ''

# Apply styling and display
styled_df = df.style.applymap(highlight_returns)
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Additional insights
st.markdown("---")
st.subheader("📈 Quick Insights")

col1, col2 = st.columns(2)

with col1:
    best_performer = max(portfolio_data, key=lambda x: float(x["Return (%)"].replace('%', '').replace('+', '')))
    st.success(f"🏆 Best Performer: {best_performer['Stock']} ({best_performer['Return (%)']})")

with col2:
    worst_performer = min(portfolio_data, key=lambda x: float(x["Return (%)"].replace('%', '').replace('+', '')))
    st.error(f"📉 Worst Performer: {worst_performer['Stock']} ({worst_performer['Return (%)']})")

# Footer
st.markdown("---")
st.markdown("*Data sourced from Screener.in • Updates every 5 minutes*")
```

if **name** == “**main**”:
main()
