import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set Streamlit page configuration
st.set_page_config(page_title="Cryptocurrency Dashboard", layout="wide", page_icon="📊")

# Function to merge Binance datasets
@st.cache_data
def load_and_merge_data(folder_path="Binance Data/"):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    df_list = []
    for file in csv_files:
        try:
            df = pd.read_csv(os.path.join(folder_path, file))
            df.rename(columns={'Volume ADA': 'Volume', 'Volume BNB': 'Volume', 'Volume BTC': 'Volume',
                               'Volume DOGE': 'Volume', 'Volume DOT': 'Volume', 'Volume ETH': 'Volume',
                               'Volume LINK': 'Volume', 'Volume LTC': 'Volume', 'Volume SOL': 'Volume',
                               'Volume XRP': 'Volume'}, inplace=True)
            df_list.append(df)
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")
    
    if df_list:
        merged_df = pd.concat(df_list, ignore_index=True)
        merged_df = merged_df[['Unix', 'Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'Volume USDT', 'tradecount']]
        return merged_df
    else:
        return pd.DataFrame()

df = load_and_merge_data()

# Dictionary for coin descriptions
coin_descriptions = {
    "BTC": "Bitcoin - The first and most popular cryptocurrency.",
    "ETH": "Ethereum - A blockchain for smart contracts.",
    "BNB": "Binance Coin - The native token of Binance exchange.",
    "ADA": "Cardano - A proof-of-stake blockchain platform.",
    "DOGE": "Dogecoin - A meme coin that gained popularity.",
    "XRP": "XRP - A digital payment protocol.",
    "LTC": "Litecoin - A faster alternative to Bitcoin.",
    "DOT": "Polkadot - A multi-chain blockchain platform.",
    "SOL": "Solana - A high-performance blockchain.",
    "LINK": "Chainlink - A decentralized oracle network."
}
# Sidebar Navigation
st.sidebar.title("📌 Dashboard Guide")
page = st.sidebar.radio("Go to:", ["Overview", "Growth", "Crypto Battle", "Market Fluctuations", "Volume Analysis", "Trade Count", "All Coins Comparison"])

if page == "Overview":
    st.markdown("<h1>📊 Cryptocurrency Market Overview</h1>", unsafe_allow_html=True)
    st.markdown("<h2>🔍 An Interactive Dashboard to Analyze Cryptocurrency Trends</h2>", unsafe_allow_html=True)
    
    selected_coin = st.selectbox("🔹 Select Coin:", sorted(df["Symbol"].unique()))
    selected_year = st.selectbox("📅 Select Year:", sorted(df["Date"].str[:4].unique()))
    selected_month = st.selectbox("📆 Select Month:", [str(i).zfill(2) for i in range(1, 13)])
    selected_day = st.selectbox("📊 Select Day:", [str(i).zfill(2) for i in range(1, 32)])
    
    filtered_df = df[(df["Symbol"] == selected_coin) &
                     (df["Date"].str[:4] == selected_year) &
                     (df["Date"].str[5:7] == selected_month) &
                     (df["Date"].str[8:10] == selected_day)]
    
    if not filtered_df.empty:
        selected_price = filtered_df.iloc[-1]['Close']
        # Ensure selected_coin matches dictionary keys correctly
        selected_coin = selected_coin.upper()  # Standardizing selection
        #description = coin_descriptions.get(selected_coin)
        st.markdown(f"<h2>💰 Price of {selected_coin} on {selected_day}-{selected_month}-{selected_year}: ${selected_price}</h2>", unsafe_allow_html=True)
        #st.markdown(f"<h3>ℹ️ {description}</h3>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please select all options to view data.")
  
    
    # Show the last 7 days' prices as a bar graph with different colors
    last_7_days_df = df[(df["Symbol"] == selected_coin)].sort_values("Date").tail(7)
    if not last_7_days_df.empty:
        colors = px.colors.qualitative.Set1[:7]  # Using different colors for each bar
        fig_bar = px.bar(last_7_days_df, x="Date", y="Close", title=f"Last 7 Days Price of {selected_coin}", color="Date", color_discrete_sequence=colors)
        st.plotly_chart(fig_bar)


    st.markdown("<h2>📌 Key Insights</h2>", unsafe_allow_html=True)
    st.write("- 📊 Cryptocurrency market trends and insights.")
    st.write("- 📈 Market volatility and price fluctuations are significant.")
    st.write("- 🔄 Liquidity and trade volume vary across coins.")
    
    st.markdown("<h2>🛠 Developed By</h2>", unsafe_allow_html=True)
    st.write("Owais Ahmad using Streamlit and Plotly")


elif page == "Growth":
    st.markdown("<h1>📈 Cryptocurrency Growth Analysis</h1>", unsafe_allow_html=True)
    
    # Select a single coin
    coin_options = sorted(df["Symbol"].unique())
    selected_coin = st.selectbox("🔹 Select Coin:", coin_options, index=coin_options.index("BTC") if "BTC" in coin_options else 0)
    
    # Select time range
    start_year, end_year = st.select_slider(
        "📅 Select Year Range:",
        options=sorted(df["Date"].str[:4].unique()),
        value=(min(df["Date"].str[:4]), max(df["Date"].str[:4]))
    )
    
    # Toggle for Price vs. Percentage Growth
    growth_type = st.radio("📊 Growth Type:", ["Absolute Price", "Percentage Growth"])
    
    # Toggle for time scale
    time_scale = st.radio("⏳ Time Scale:", ["Daily", "Monthly", "Yearly"])
    
    # Convert Date to datetime format
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Filter data for the selected coin
    filtered_df = df[(df["Symbol"] == selected_coin) & (df["Date"].dt.year >= int(start_year)) & (df["Date"].dt.year <= int(end_year))]
    
    if time_scale == "Monthly":
        filtered_df["Date"] = filtered_df["Date"].dt.to_period("M").astype(str)
        filtered_df = filtered_df.groupby("Date", as_index=False).mean(numeric_only=True)
    elif time_scale == "Yearly":
        filtered_df["Date"] = filtered_df["Date"].dt.to_period("Y").astype(str)
        filtered_df = filtered_df.groupby("Date", as_index=False).mean(numeric_only=True)
    
    if growth_type == "Percentage Growth":
        filtered_df["Close"] = (filtered_df["Close"] - filtered_df["Close"].iloc[0]) / filtered_df["Close"].iloc[0] * 100
    
    fig = px.line(filtered_df, x="Date", y="Close", title=f"{growth_type} of {selected_coin} from {start_year} to {end_year}", labels={"Close": growth_type})
    fig.update_traces(mode="lines+markers")
    
    st.plotly_chart(fig)



elif page == "Crypto Battle":
    st.markdown("<h1>📊 Cryptocurrency Comparison</h1>", unsafe_allow_html=True)
    
    selected_coins = st.multiselect("🔹 Select Coins:", sorted(df["Symbol"].unique()))
    start_year = st.selectbox("📅 Start Year:", sorted(df["Date"].str[:4].unique()))
    end_year = st.selectbox("📅 End Year:", sorted(df["Date"].str[:4].unique()))
    
    growth_type = st.radio("📊 Growth Type:", ["Absolute Growth", "Percentage Growth"])
    chart_type = st.radio("📈 Chart Type:", ["Bar Chart", "Line Chart"])
    
    filtered_df = df[(df["Symbol"].isin(selected_coins)) &
                     (df["Date"].str[:4] >= start_year) & (df["Date"].str[:4] <= end_year)]
    
    filtered_df = filtered_df.groupby("Symbol", as_index=False).agg({"Close": "mean"})
    
    if growth_type == "Percentage Growth":
        filtered_df["Close"] = (filtered_df["Close"] - filtered_df["Close"].min()) / filtered_df["Close"].min() * 100
    
    if chart_type == "Bar Chart":
        fig = px.bar(filtered_df, x="Symbol", y="Close", color="Symbol", title="Comparison of Cryptocurrency Growth")
    else:
        fig = px.line(filtered_df, x="Symbol", y="Close", markers=True, title="Comparison of Cryptocurrency Growth")
    
    st.plotly_chart(fig)




elif page == "Market Fluctuations":
    st.markdown("<h1>📊 Market Fluctuations: Open vs Close</h1>", unsafe_allow_html=True)
    
    available_coins = sorted(df["Symbol"].unique())
    default_coin = ["BTC"] if "BTC" in available_coins else [available_coins[0]]
    
    selected_coins = st.multiselect("🔹 Select Coin(s):", available_coins, default=default_coin)
    start_year = st.selectbox("📅 Start Year:", sorted(df["Date"].str[:4].unique()))
    end_year = st.selectbox("📅 End Year:", sorted(df["Date"].str[:4].unique()))
    
    filtered_df = df[(df["Symbol"].isin(selected_coins)) &
                     (df["Date"].str[:4] >= start_year) & (df["Date"].str[:4] <= end_year)]
    
    filtered_df["Price Change"] = filtered_df["Close"] - filtered_df["Open"]
    
    # Sorting by absolute price change for better visual clarity
    filtered_df = filtered_df.groupby("Symbol")["Price Change"].mean().reset_index()
    filtered_df = filtered_df.sort_values(by="Price Change", ascending=False)
    
    fig = px.bar(filtered_df, x="Symbol", y="Price Change", color="Price Change", 
                 title="Open vs Close Price Difference Across Cryptocurrencies", 
                 color_continuous_scale=["red", "green"], 
                 labels={"Symbol": "Cryptocurrency", "Price Change": "Price Difference (Close - Open)"})
    
    fig.update_traces(text=filtered_df["Price Change"].round(2), textposition='outside')
    
    st.plotly_chart(fig)







elif page == "Volume Analysis":
    st.markdown("<h1>📊 Cryptocurrency Volume Analysis</h1>", unsafe_allow_html=True)
    
    available_coins = sorted(df["Symbol"].unique())
    selected_coins = st.multiselect("🔹 Select Coin(s):", available_coins, default=available_coins[:5])
    start_year = st.selectbox("📅 Start Year:", sorted(df["Date"].str[:4].unique()))
    end_year = st.selectbox("📅 End Year:", sorted(df["Date"].str[:4].unique()))
    
    filtered_df = df[(df["Symbol"].isin(selected_coins)) &
                     (df["Date"].str[:4] >= start_year) & (df["Date"].str[:4] <= end_year)]
    
    # Calculate average trading volume per year per coin
    filtered_df["Year"] = filtered_df["Date"].str[:4]
    avg_volume_df = filtered_df.groupby(["Symbol", "Year"])["Volume"].mean().reset_index()
    
    # Identify top and bottom traded coins
    top_coin = avg_volume_df.loc[avg_volume_df["Volume"].idxmax()]
    bottom_coin = avg_volume_df.loc[avg_volume_df["Volume"].idxmin()]
    
    # Display insights
    st.markdown(f"**🔝 Most Traded Coin:** {top_coin['Symbol']} with Avg Volume: {top_coin['Volume']:.2f}")
    st.markdown(f"**🔻 Least Traded Coin:** {bottom_coin['Symbol']} with Avg Volume: {bottom_coin['Volume']:.2f}")  
    # Bar Chart: Volume Comparison Across Cryptocurrencies
    fig_bar = px.bar(avg_volume_df, x="Symbol", y="Volume", color="Symbol", 
                     title="Average Trading Volume Across Cryptocurrencies", 
                     labels={"Volume": "Average Trading Volume"}, 
                     text_auto=True)
    
    # Line Chart: Volume Trend Over Time
    fig_line = px.line(filtered_df, x="Date", y="Volume", color="Symbol", 
                      title="Volume Trend Over Time", markers=True, 
                      labels={"Volume": "Trading Volume"})
    # Display Charts
    col1, col2 = st.columns(2)
    with col1: st.plotly_chart(fig_bar)
    with col2: st.plotly_chart(fig_line)
elif page == "Trade Count":
    st.markdown("<h1>📊 Trade Count Analysis</h1>", unsafe_allow_html=True)    
    fig_bar = px.bar(df, x="Symbol", y="tradecount", color="Symbol", title="Trade Count of Cryptocurrencies")
    fig_pie = px.pie(df, values="tradecount", names="Symbol", title="Trade Count Distribution")    
    col1, col2 = st.columns(2)
    with col1: st.plotly_chart(fig_bar)
    with col2: st.plotly_chart(fig_pie)
elif page == "All Coins Comparison":
    st.markdown("<h1>📊 Market Capitalization Comparison</h1>", unsafe_allow_html=True)   
    df["Market Cap"] = df["Close"] * df["Volume"]  # Calculate Market Cap    
    fig_pie = px.pie(df, values="Market Cap", names="Symbol", title="Market Share of All Coins")
    fig_bar = px.bar(df, x="Symbol", y="Market Cap", color="Symbol", title="Comparison of Market Cap Across Coins")    
    col1, col2 = st.columns(2)
    with col1: st.plotly_chart(fig_pie)
    with col2: st.plotly_chart(fig_bar)



