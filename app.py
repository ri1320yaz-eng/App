


import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime

# Set page config for mobile compatibility
st.set_page_config(
    page_title="Motilal Midcap Fund Real time returns",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    /* Mobile-first responsive design */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Adjust metrics for mobile */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
    }
    
    /* Make buttons full width on mobile */
    .stButton > button {
        width: 100%;
        margin: 0.25rem 0;
    }
    
    /* Adjust expander styling */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
    }
    
    /* Make dataframe scrollable on mobile */
    .dataframe {
        font-size: 0.8rem;
    }
    
    /* Responsive text */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.2rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for stock data
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = {
        "DIXON": {"url": "https://www.screener.in/company/DIXON/consolidated/", "allocation": 10.08},
        "COFORGE": {"url": "https://www.screener.in/company/COFORGE/consolidated/", "allocation": 9.79},
        "TRENT": {"url": "https://www.screener.in/company/TRENT/consolidated/", "allocation": 9.14},
        "ETERNAL": {"url": "https://www.screener.in/company/ETERNAL/consolidated/", "allocation": 9.03},
        "KALYANKJIL": {"url": "https://www.screener.in/company/KALYANKJIL/consolidated/", "allocation": 8.70},
        "PAYTM": {"url": "https://www.screener.in/company/PAYTM/consolidated/", "allocation": 8.68},
        "PERSISTENT": {"url": "https://www.screener.in/company/PERSISTENT/consolidated/", "allocation": 8.39},
        "POLYCAB": {"url": "https://www.screener.in/company/POLYCAB/consolidated/", "allocation": 6.22},
        "KEI": {"url": "https://www.screener.in/company/KEI/", "allocation": 4.11},
        "KAYNES": {"url": "https://www.screener.in/company/KAYNES/consolidated/", "allocation": 3.70},
        "BHARTIHEXA": {"url": "https://www.screener.in/company/BHARTIHEXA/", "allocation": 3.34},
        "MAXHEALTH": {"url": "https://www.screener.in/company/MAXHEALTH/consolidated/", "allocation": 3.21},
        "ABCAPITAL": {"url": "https://www.screener.in/company/ABCAPITAL/consolidated/", "allocation": 3.20},
        "TIINDIA": {"url": "https://www.screener.in/company/TIINDIA/consolidated/", "allocation": 2.98},
        "PRESTIGE": {"url": "https://www.screener.in/company/PRESTIGE/consolidated/", "allocation": 2.58},
        "SUPREMEIND": {"url": "https://www.screener.in/company/SUPREMEIND/consolidated/", "allocation": 2.38},
        "KPITTECH": {"url": "https://www.screener.in/company/KPITTECH/consolidated/", "allocation": 1.03},
        "POWERINDIA": {"url": "https://www.screener.in/company/POWERINDIA", "allocation": 0.86}
    }

# App title - more compact for mobile
st.title("📈 Portfolio Tracker")
st.markdown("*Real-time stock returns*")
st.markdown("*By - Riyaz M*")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_return(url, stock_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Use regex to find the first occurrence of a percentage value
        match = re.search(r"[+-]?[0-9]+\.[0-9]+(?=%)", soup.text)
        if match:
            return float(match.group())
        else:
            return 0.0
    except Exception as e:
        st.error(f"Error fetching {stock_name}: {str(e)}")
        return 0.0

def calculate_portfolio_return():
    portfolio_data = []
    total_allocation = sum(data["allocation"] for data in st.session_state.stock_data.values())
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_weighted_return = 0
    
    for i, (stock_name, data) in enumerate(st.session_state.stock_data.items()):
        status_text.text(f'Fetching {stock_name}...')
        stock_return = fetch_stock_return(data["url"], stock_name)
        normalized_allocation = data["allocation"] / total_allocation if total_allocation > 0 else 0
        weighted_return = stock_return * normalized_allocation
        total_weighted_return += weighted_return
        
        portfolio_data.append({
            "Stock": stock_name,
            "Return": f"{stock_return:+.2f}%",
            "Weight": f"{data['allocation']:.1f}%",
            "Contribution": f"{weighted_return:+.3f}%"
        })
        
        # Update progress
        progress_bar.progress((i + 1) / len(st.session_state.stock_data))
        time.sleep(0.1)
    
    progress_bar.empty()
    status_text.empty()
    
    return portfolio_data, total_weighted_return

# Create tabs for different sections
tab1, tab2 = st.tabs(["📊 Portfolio", "⚙️ Manage"])

with tab1:
    # Mobile-friendly header with stacked layout
    st.button("🔄 Refresh Data", type="primary", use_container_width=True)
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    if len(st.session_state.stock_data) > 0:
        with st.spinner("Loading portfolio..."):
            portfolio_data, total_return = calculate_portfolio_return()
        
        # Mobile-friendly metrics - single column layout
        st.metric(
            label="📈 Portfolio Return Today",
            value=f"{total_return:+.2f}%",
            delta=None
        )
        
        # Two-column layout for secondary metrics
        col1, col2 = st.columns(2)
        
        with col1:
            positive_stocks = len([stock for stock in portfolio_data if float(stock["Return"].replace('%', '').replace('+', '')) > 0])
            st.metric(
                label="Green Stocks",
                value=f"{positive_stocks}/{len(portfolio_data)}"
            )
        
        with col2:
            total_allocation = sum(data["allocation"] for data in st.session_state.stock_data.values())
            st.metric(
                label="Total Weight",
                value=f"{total_allocation:.0f}%"
            )
        
        st.markdown("---")
        
        # Mobile-optimized stock performance
        st.subheader("📊 Stock Performance")
        
        # Create mobile-friendly DataFrame with shorter column names
        df = pd.DataFrame(portfolio_data)
        
        # Style the dataframe for mobile
        def highlight_returns(val):
            if isinstance(val, str) and '%' in val and 'Return' in str(val):
                try:
                    numeric_val = float(val.replace('%', '').replace('+', ''))
                    if numeric_val > 0:
                        return 'background-color: #d4edda; color: #155724'
                    elif numeric_val < 0:
                        return 'background-color: #f8d7da; color: #721c24'
                except:
                    pass
            return ''
        
        # Display with mobile-friendly settings
        styled_df = df.style.applymap(highlight_returns)
        st.dataframe(
            styled_df, 
            use_container_width=True, 
            hide_index=True,
            height=400  # Fixed height for mobile scrolling
        )
        
        # Mobile-friendly insights
        st.markdown("---")
        st.subheader("📈 Today's Highlights")
        
        best_performer = max(portfolio_data, key=lambda x: float(x["Return"].replace('%', '').replace('+', '')))
        worst_performer = min(portfolio_data, key=lambda x: float(x["Return"].replace('%', '').replace('+', '')))
        
        # Stack insights vertically for mobile
        st.success(f"🏆 **Best**: {best_performer['Stock']} ({best_performer['Return']})")
        st.error(f"📉 **Worst**: {worst_performer['Stock']} ({worst_performer['Return']})")
    
    else:
        st.warning("📱 No stocks in portfolio. Add stocks in the 'Manage' tab.")

with tab2:
    st.subheader("⚙️ Portfolio Management")
    
    # Mobile-friendly add stock section
    st.markdown("### ➕ Add Stock")
    
    # Stack inputs vertically for mobile
    new_stock_symbol = st.text_input("Stock Symbol", placeholder="e.g., RELIANCE", key="new_stock")
    new_stock_url = st.text_input("Screener URL", placeholder="https://www.screener.in/company/RELIANCE/", key="new_url")
    new_allocation = st.number_input("Weight %", min_value=0.01, max_value=100.0, value=1.0, step=0.1, key="new_allocation")
    
    if st.button("➕ Add to Portfolio", type="primary", use_container_width=True):
        if new_stock_symbol and new_stock_url:
            if new_stock_symbol.upper() not in st.session_state.stock_data:
                st.session_state.stock_data[new_stock_symbol.upper()] = {
                    "url": new_stock_url,
                    "allocation": new_allocation
                }
                st.success(f"✅ Added {new_stock_symbol.upper()}!")
                st.rerun()
            else:
                st.error(f"❌ {new_stock_symbol.upper()} already exists!")
        else:
            st.error("❌ Please fill in both fields!")
    
    st.markdown("---")
    
    # Mobile-friendly edit section
    st.markdown("### ✏️ Edit Stocks")
    
    if len(st.session_state.stock_data) > 0:
        # Mobile-optimized stock editing
        for stock, data in st.session_state.stock_data.items():
            with st.expander(f"📈 {stock} ({data['allocation']:.1f}%)"):
                # Stack form elements vertically
                new_url = st.text_input("URL", value=data['url'], key=f"url_{stock}")
                new_alloc = st.number_input("Weight %", min_value=0.01, max_value=100.0, 
                                          value=data['allocation'], step=0.1, key=f"alloc_{stock}")
                
                # Mobile-friendly button layout
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Update", key=f"update_{stock}", use_container_width=True):
                        st.session_state.stock_data[stock]['url'] = new_url
                        st.session_state.stock_data[stock]['allocation'] = new_alloc
                        st.success(f"✅ Updated {stock}!")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{stock}", use_container_width=True):
                        del st.session_state.stock_data[stock]
                        st.success(f"✅ Deleted {stock}!")
                        st.rerun()
        
        st.markdown("---")
        
        # Mobile-friendly portfolio summary
        total_allocation = sum(data["allocation"] for data in st.session_state.stock_data.values())
        st.markdown("### 📊 Summary")
        
        # Single column layout for mobile
        st.metric("Total Stocks", len(st.session_state.stock_data))
        st.metric("Total Weight", f"{total_allocation:.1f}%")
        
        if abs(total_allocation - 100) > 1:
            st.warning(f"⚠️ Total weight: {total_allocation:.1f}%. Consider adjusting to 100%.")
    
    else:
        st.info("📱 No stocks yet. Add your first stock above!")

# Mobile-friendly footer
st.markdown("---")
st.caption("*Data from Screener.in • Updates every 5min*")
