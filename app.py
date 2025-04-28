import streamlit as st
import pandas as pd
import os
import altair as alt
from io import BytesIO

# --- Set up page config ---
st.set_page_config(page_title="Mutual Funds Explorer", layout="wide", initial_sidebar_state="expanded")

# --- Paths ---
funds_folder = "test/"  # Path where all schemeCode.csv are stored
master_csv_path = "all_mf.csv"  # Master file with schemeName and schemeCode

# --- Load Master Data ---
@st.cache_data
def load_master():
    return pd.read_csv(master_csv_path)

master_data = load_master()

# --- Search Section ---
st.title("💸 Mutual Funds Dashboard")

st.markdown("### 🔍 Search Mutual Funds")
search_term = st.text_input("Enter Fund Name", placeholder="Type to search...")

# --- Filter master_data based on search ---
if search_term:
    filtered_data = master_data[master_data['schemeName'].str.contains(search_term, case=False, na=False)]
else:
    filtered_data = master_data

st.write(f"### Showing {len(filtered_data)} funds")

# --- Fund Selection ---
selection_mode = st.radio("Select Mode", ("Individual Fund", "Compare Funds"))

if selection_mode == "Individual Fund":
    # --- Individual Fund Analysis ---
    selected_fund = st.selectbox(
        "Select a Mutual Fund to Analyze",
        filtered_data['schemeName'].tolist(),
        key="fund_select",
        help="Start typing to quickly search"
    )

    # --- If fund is selected ---
    if selected_fund:
        st.markdown("---")
        st.header(f"Details for {selected_fund}")

        # --- Get corresponding schemeCode ---
        selected_code = master_data[master_data['schemeName'] == selected_fund]['schemeCode'].values[0]
        fund_csv_path = os.path.join(funds_folder, f"{selected_code}.csv")
        
        if os.path.exists(fund_csv_path):
            fund_data = pd.read_csv(fund_csv_path)

            # --- Preprocessing ---
            fund_data['date'] = pd.to_datetime(fund_data['date'], format='%d-%m-%Y', errors='coerce')
            fund_data['nav'] = pd.to_numeric(fund_data['nav'], errors='coerce')
            fund_data = fund_data.dropna(subset=['date', 'nav'])
            fund_data = fund_data.sort_values('date')

            # --- Advanced Calculations ---
            fund_data['cum_return'] = fund_data['nav'] / fund_data['nav'].iloc[0] - 1
            fund_data['nav_7d_ma'] = fund_data['nav'].rolling(window=7).mean()
            fund_data['nav_30d_ma'] = fund_data['nav'].rolling(window=30).mean()

            # Fix for KeyError: 'volatility_30d' and 'drawdown'
            # Ensure these columns are calculated before accessing them
            if 'volatility_30d' not in fund_data.columns:
                fund_data['volatility_30d'] = fund_data['nav'].rolling(window=30).std()

            if 'drawdown' not in fund_data.columns:
                fund_data['drawdown'] = (fund_data['nav'] - fund_data['nav'].cummax()) / fund_data['nav'].cummax()

            # --- Performance Analysis Charts ---
            st.markdown("### 📈 Performance Analysis Charts")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["NAV Growth", "Cumulative Returns", "Moving Averages", "Volatility", "Drawdowns"])

            with tab1:
                st.subheader("📈 NAV Growth Over Time")
                nav_chart = alt.Chart(fund_data).mark_line(color="blue").encode(
                    x='date:T',
                    y='nav:Q',
                    tooltip=['date:T', 'nav:Q']
                ).properties(
                    width=800,
                    height=400
                ).interactive()
                st.altair_chart(nav_chart)

            with tab2:
                st.subheader("📈 Cumulative Returns")
                cum_chart = alt.Chart(fund_data).mark_area(color="green", opacity=0.5).encode(
                    x='date:T',
                    y='cum_return:Q',
                    tooltip=['date:T', 'cum_return:Q']
                ).properties(
                    width=800,
                    height=400
                ).interactive()
                st.altair_chart(cum_chart)

            with tab3:
                st.subheader("📊 7-Day and 30-Day Moving Averages")
                ma_chart = alt.Chart(fund_data).transform_fold(
                    ['nav_7d_ma', 'nav_30d_ma'],
                    as_=['Moving Average', 'NAV']
                ).mark_line().encode(
                    x='date:T',
                    y='NAV:Q',
                    color='Moving Average:N',
                    tooltip=['date:T', 'NAV:Q', 'Moving Average:N']
                ).properties(
                    width=800,
                    height=400
                ).interactive()
                st.altair_chart(ma_chart)

            with tab4:
                st.subheader("📉 Volatility (30-Day Rolling Std Dev)")
                vol_chart = alt.Chart(fund_data).mark_area(color="red", opacity=0.4).encode(
                    x='date:T',
                    y='volatility_30d:Q',
                    tooltip=['date:T', 'volatility_30d:Q']
                ).properties(
                    width=800,
                    height=400
                ).interactive()
                st.altair_chart(vol_chart)

            with tab5:
                st.subheader("📉 Drawdowns")
                drawdown_chart = alt.Chart(fund_data).mark_area(color="orange", opacity=0.4).encode(
                    x='date:T',
                    y='drawdown:Q',
                    tooltip=['date:T', 'drawdown:Q']
                ).properties(
                    width=800,
                    height=400
                ).interactive()
                st.altair_chart(drawdown_chart)

            # --- Risk vs Return Chart (Updated) ---
            st.markdown("### 📊 Risk vs Return")
            risk_return_data = fund_data[['cum_return', 'volatility_30d']].dropna()
            risk_return_chart = alt.Chart(risk_return_data).mark_circle(size=150, color="purple", opacity=0.6).encode(
                x=alt.X('volatility_30d:Q', title="Risk (30-Day Volatility)"),
                y=alt.Y('cum_return:Q', title="Return (Cumulative Return)"),
                tooltip=['cum_return:Q', 'volatility_30d:Q']
            ).properties(
                width=600,
                height=400
            ).interactive()
            st.altair_chart(risk_return_chart)

            # --- Quick Performance Metrics ---
            st.markdown("### 📋 Performance Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current NAV", f"₹{fund_data['nav'].iloc[-1]:.2f}")
            with col2:
                st.metric("Total Return", f"{(fund_data['cum_return'].iloc[-1]*100):.2f}%")
            with col3:
                st.metric("30-Day Volatility", f"{fund_data['volatility_30d'].iloc[-1]:.4f}")

        else:
            st.error("⚠️ Fund NAV data not found! Please check if the CSV file exists.")

elif selection_mode == "Compare Funds":
    # --- Compare Multiple Funds ---
    selected_funds = st.multiselect(
        "Select Mutual Funds to Compare",
        filtered_data['schemeName'].tolist(),
        help="Select funds for comparison"
    )

    if len(selected_funds) >= 2:
        comparison_data = []
        
        for fund in selected_funds:
            selected_code = master_data[master_data['schemeName'] == fund]['schemeCode'].values[0]
            fund_csv_path = os.path.join(funds_folder, f"{selected_code}.csv")
            
            if os.path.exists(fund_csv_path):
                fund_data = pd.read_csv(fund_csv_path)

                # --- Preprocessing ---
                fund_data['date'] = pd.to_datetime(fund_data['date'], format='%d-%m-%Y', errors='coerce')
                fund_data['nav'] = pd.to_numeric(fund_data['nav'], errors='coerce')
                fund_data = fund_data.dropna(subset=['date', 'nav'])
                fund_data = fund_data.sort_values('date')

                # --- Advanced Calculations ---
                fund_data['cum_return'] = fund_data['nav'] / fund_data['nav'].iloc[0] - 1
                fund_data['nav_7d_ma'] = fund_data['nav'].rolling(window=7).mean()
                fund_data['nav_30d_ma'] = fund_data['nav'].rolling(window=30).mean()
                fund_data['volatility_30d'] = fund_data['nav'].rolling(window=30).std()
                fund_data['drawdown'] = fund_data['nav'] / fund_data['nav'].cummax() - 1  # Drawdown

                # Add schemeName for comparison
                fund_data['schemeName'] = fund

                comparison_data.append(fund_data)

        if comparison_data:
            # --- Combine Data for Comparison ---
            comparison_df = pd.concat(comparison_data, keys=selected_funds)

            # --- NAV Growth Chart ---
            comparison_nav_chart = alt.Chart(comparison_df.reset_index()).mark_line().encode(
                x='date:T',
                y='nav:Q',
                color='schemeName:N',
                tooltip=['schemeName:N', 'date:T', 'nav:Q']
            ).properties(
                width=800,
                height=400
            ).interactive()
            st.altair_chart(comparison_nav_chart)

            # --- Cumulative Returns Comparison Chart ---
            st.markdown("### 📈 Cumulative Returns Comparison")
            cum_return_chart = alt.Chart(comparison_df.reset_index()).mark_area().encode(
                x='date:T',
                y='cum_return:Q',
                color='schemeName:N',
                tooltip=['schemeName:N', 'date:T', 'cum_return:Q']
            ).properties(
                width=800,
                height=400
            ).interactive()
            st.altair_chart(cum_return_chart)

            # --- Moving Averages Comparison ---
            st.markdown("### 📊 7-Day and 30-Day Moving Averages Comparison")
            ma_chart = alt.Chart(comparison_df.reset_index()).transform_fold(
                ['nav_7d_ma', 'nav_30d_ma'],
                as_=['Moving Average', 'NAV']
            ).mark_line().encode(
                x='date:T',
                y='NAV:Q',
                color='Moving Average:N',
                tooltip=['date:T', 'NAV:Q', 'Moving Average:N']
            ).properties(
                width=800,
                height=400
            ).interactive()
            st.altair_chart(ma_chart)

            # --- Volatility Comparison ---
            st.markdown("### 📉 Volatility Comparison (30-Day Rolling Std Dev)")
            vol_chart = alt.Chart(comparison_df.reset_index()).mark_area(opacity=0.4).encode(
                x='date:T',
                y='volatility_30d:Q',
                color='schemeName:N',
                tooltip=['schemeName:N', 'date:T', 'volatility_30d:Q']
            ).properties(
                width=800,
                height=400
            ).interactive()
            st.altair_chart(vol_chart)

            # --- Risk vs Return Comparison Chart ---
            st.markdown("### 📊 Risk vs Return Comparison")
            risk_return_data = comparison_df[['schemeName', 'cum_return', 'volatility_30d']].dropna()
            risk_return_chart = alt.Chart(risk_return_data).mark_circle(size=150, opacity=0.6).encode(
                x=alt.X('volatility_30d:Q', title="Risk (30-Day Volatility)"),
                y=alt.Y('cum_return:Q', title="Return (Cumulative Return)"),
                color='schemeName:N',
                tooltip=['schemeName:N', 'cum_return:Q', 'volatility_30d:Q']
            ).properties(
                width=800,
                height=400
            ).interactive()
            st.altair_chart(risk_return_chart)

            # --- Drawdown Comparison Chart ---
            st.markdown("### 📉 Drawdown Comparison")
            comparison_drawdown_data = comparison_df[['schemeName', 'drawdown']].dropna()
            drawdown_chart = alt.Chart(comparison_drawdown_data).mark_area(opacity=0.4).encode(
                x='date:T',
                y='drawdown:Q',
                color='schemeName:N',
                tooltip=['schemeName:N', 'date:T', 'drawdown:Q']
            ).properties(
                width=800,
                height=400
            ).interactive()
            st.altair_chart(drawdown_chart)

            # --- Performance Summary for Comparison ---
            st.markdown("### 📋 Comparison Summary")
            comparison_summary = pd.DataFrame({
                'Fund Name': selected_funds,
                'Latest NAV': [df['nav'].iloc[-1] for df in comparison_data],
                'Total Return': [(df['nav'].iloc[-1] / df['nav'].iloc[0] - 1) * 100 for df in comparison_data],
                '30-Day Volatility': [df['volatility_30d'].iloc[-1] for df in comparison_data],
            })
            st.write(comparison_summary)

        else:
            st.warning("No valid data found for selected funds.")

    else:
        st.warning("Please select at least 2 funds for comparison.")

# --- Footer ---
st.markdown("---")
st.markdown("All rights reserved &copy; 2025 . Application is build by TeluguReality.Org. Contact yaswanthreddypanem@gmail.com")
