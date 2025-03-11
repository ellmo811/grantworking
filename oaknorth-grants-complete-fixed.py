import streamlit as st
import pandas as pd
import numpy as np

# Set page config first before any other Streamlit commands
st.set_page_config(
    page_title="OakNorth Grants Analysis - Various Redemption Rates",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display the main title
st.title("OakNorth Grants Analysis - Various Redemption Rates")
st.markdown("This tool allows you to analyze the impact of different redemption rates on OakNorth grants value.")

# Sidebar for inputs
st.sidebar.header("Input Parameters")

# PBT Growth Rate
pbt_growth_rate = st.sidebar.slider(
    "PBT Growth Rate", 
    min_value=10, 
    max_value=25,
    value=20,
    step=1,
    help="Annual growth rate of share price"
) / 100

# Common Share section
st.sidebar.header("Common Share")

# Common share redemption percentage using slider
common_redemption_rate = st.sidebar.slider(
    "Common Share Redemption Percentage", 
    min_value=0, 
    max_value=10,
    value=5,
    step=1,
    help="Percentage of common shares to redeem each year starting from 2026"
) / 100

# Get total common shares
total_common_shares = st.sidebar.number_input(
    "Total Common Shares",
    min_value=1,
    value=30000,
    step=100,
    help="Total number of common shares"
)

# Common share purchase price
common_purchase_price = st.sidebar.number_input(
    "Common Share Purchase Price (£)",
    min_value=0.01,
    value=2.00,
    step=0.01,
    format="%.2f",
    help="Initial purchase price of common shares"
)

# A-Share / Options section
st.sidebar.header("A-Share / Options")

# A-Share/Options redemption percentage using slider
option_redemption_rate = st.sidebar.slider(
    "A-Share/Options Redemption Percentage", 
    min_value=0, 
    max_value=10,
    value=5,
    step=1,
    help="Percentage of vested unsold A-Share/Options to redeem each year"
) / 100

# Get strike price
strike_price = st.sidebar.number_input(
    "Strike Price (£)",
    min_value=0.01,
    value=6.00,
    step=0.01,
    format="%.2f",
    help="Initial strike price of options"
)

# Get total grant shares
total_grant_shares = st.sidebar.number_input(
    "Total Grant Shares",
    min_value=1,
    value=100000,
    step=100,
    help="Total number of shares in the grant"
)

# Vesting schedule inputs
st.sidebar.subheader("Vesting Schedule")
vesting_method = st.sidebar.radio(
    "Vesting Method",
    ["Default Schedule", "Custom Vesting"],
    help="Choose default vesting schedule or set custom values"
)

# Initialize vested_shares_input dictionary with all years
years_range = range(2025, 2036)
vested_shares_input = {year: 0 for year in years_range}

if vesting_method == "Default Schedule":
    # Default vesting schedule
    default_values = {
        2025: 60000,
        2026: 70000,
        2027: 80000,
        2028: 90000,
        2029: 100000
    }
    # Fill in the dictionary with default values
    for year in years_range:
        if year in default_values:
            vested_shares_input[year] = default_values[year]
        else:
            vested_shares_input[year] = 100000  # All years after 2029 are fully vested
    
    # Display the default schedule
    st.sidebar.write("Default vesting schedule:")
    default_schedule = pd.DataFrame({
        "Year": list(vested_shares_input.keys()), 
        "Vested Shares": list(vested_shares_input.values())
    })
    st.sidebar.dataframe(default_schedule, hide_index=True)
    
else:
    # Custom vesting inputs
    st.sidebar.write("Enter vested shares for each year:")
    
    # Use columns for more compact layout
    col1, col2 = st.sidebar.columns(2)
    
    # Year distribution between columns
    first_half = list(years_range)[:len(list(years_range))//2 + 1]
    second_half = list(years_range)[len(list(years_range))//2 + 1:]
    
    with col1:
        for year in first_half:
            default_value = 60000 if year == 2025 else 70000 if year == 2026 else 80000 if year == 2027 else 90000 if year == 2028 else 100000
            vested_shares_input[year] = st.number_input(
                f"{year}", 
                min_value=0, 
                max_value=int(total_grant_shares), 
                value=default_value, 
                step=100,
                key=f"vest_{year}"
            )
    
    with col2:
        for year in second_half:
            vested_shares_input[year] = st.number_input(
                f"{year}", 
                min_value=0, 
                max_value=int(total_grant_shares), 
                value=100000, 
                step=100,
                key=f"vest_{year}"
            )

# Function to calculate results for specific redemption rates
def calculate_results(common_redemption_rate, option_redemption_rate):
    years = list(range(2024, 2036))
    results = {}
    
    # Initialize objects for all years
    for year in years:
        results[year] = {}
    
    # Calculate share price series
    results[2024]['Share Price'] = 6.00  # Base price in 2024
    for year in range(2025, 2036):
        results[year]['Share Price'] = results[year-1]['Share Price'] * (1 + pbt_growth_rate)
    
    # Common Share calculations
    for year in years:
        results[year]['Common Shares Redeemed'] = 0.0
        results[year]['Cumulative Common Redeemed'] = 0.0
        results[year]['Unsold Common Shares'] = 0.0
        results[year]['Common Redemption Value'] = 0.0
        results[year]['Cumulative Common Redemption Value'] = 0.0
        results[year]['Value of Unsold Common Shares'] = 0.0
        results[year]['Total Common Share Value'] = 0.0
    
    # Initialize 2024 values
    results[2024]['Unsold Common Shares'] = total_common_shares
    
    # 2025 calculations (no redemption in first year)
    results[2025]['Common Shares Redeemed'] = 0
    results[2025]['Cumulative Common Redeemed'] = 0
    results[2025]['Unsold Common Shares'] = total_common_shares
    results[2025]['Common Redemption Value'] = 0
    results[2025]['Cumulative Common Redemption Value'] = 0
    
    # Calculate value of unsold common shares for 2025
    common_price_diff_2025 = max(0, results[2025]['Share Price'] - common_purchase_price)
    results[2025]['Value of Unsold Common Shares'] = common_price_diff_2025 * results[2025]['Unsold Common Shares']
    results[2025]['Total Common Share Value'] = results[2025]['Value of Unsold Common Shares']
    
    # Calculate common share values for 2026-2035
    for year in range(2026, 2036):
        # Common shares redeemed this year (% of previous year's unsold shares)
        results[year]['Common Shares Redeemed'] = results[year-1]['Unsold Common Shares'] * common_redemption_rate
        
        # Cumulative common shares redeemed
        results[year]['Cumulative Common Redeemed'] = results[year-1]['Cumulative Common Redeemed'] + results[year]['Common Shares Redeemed']
        
        # Unsold common shares
        results[year]['Unsold Common Shares'] = total_common_shares - results[year]['Cumulative Common Redeemed']
        
        # Common redemption value = (share price - common purchase price) * common shares redeemed
        common_price_diff = max(0, results[year]['Share Price'] - common_purchase_price)
        results[year]['Common Redemption Value'] = common_price_diff * results[year]['Common Shares Redeemed']
        
        # Cumulative common redemption value
        results[year]['Cumulative Common Redemption Value'] = results[year-1]['Cumulative Common Redemption Value'] + results[year]['Common Redemption Value']
        
        # Value of unsold common shares
        results[year]['Value of Unsold Common Shares'] = common_price_diff * results[year]['Unsold Common Shares']
        
        # Total common share value
        results[year]['Total Common Share Value'] = results[year]['Cumulative Common Redemption Value'] + results[year]['Value of Unsold Common Shares']
    
    # A-Share/Options calculations
    for year in years:
        results[year]['Vested Shares'] = 0
        results[year]['Vested Unsold Shares'] = 0.0
        results[year]['Redeemed Shares'] = 0.0
        results[year]['Cumulative Redeemed'] = 0.0
        results[year]['Unsold Shares'] = 0.0
        results[year]['Redemption Value'] = 0.0
        results[year]['Cumulative Redemption Value'] = 0.0
        results[year]['Value of Unsold Shares'] = 0.0
        results[year]['Total Grant Value'] = 0.0
    
    # Initialize 2024 values
    results[2024]['Unsold Shares'] = total_grant_shares
    
    # 2025 calculations (no redemption in first year)
    results[2025]['Vested Shares'] = vested_shares_input[2025]
    results[2025]['Redeemed Shares'] = 0
    results[2025]['Cumulative Redeemed'] = 0
    results[2025]['Vested Unsold Shares'] = results[2025]['Vested Shares']
    results[2025]['Unsold Shares'] = total_grant_shares
    results[2025]['Redemption Value'] = 0
    results[2025]['Cumulative Redemption Value'] = 0
    
    # Calculate value of unsold shares for 2025
    share_price_diff_2025 = max(0, results[2025]['Share Price'] - strike_price)
    results[2025]['Value of Unsold Shares'] = share_price_diff_2025 * results[2025]['Unsold Shares']
    results[2025]['Total Grant Value'] = results[2025]['Value of Unsold Shares']
    
    # Calculate option values for 2026-2035
    for year in range(2026, 2036):
        # Vested shares for this year from input
        results[year]['Vested Shares'] = vested_shares_input[year]
        
        # Redeemed shares for this year (% of previous year's vested unsold shares)
        results[year]['Redeemed Shares'] = results[year-1]['Vested Unsold Shares'] * option_redemption_rate
        
        # Cumulative redeemed shares
        results[year]['Cumulative Redeemed'] = results[year-1]['Cumulative Redeemed'] + results[year]['Redeemed Shares']
        
        # Vested unsold shares = vested shares - cumulative redeemed
        results[year]['Vested Unsold Shares'] = max(0, results[year]['Vested Shares'] - results[year]['Cumulative Redeemed'])
        
        # Unsold shares = total - cumulative redeemed
        results[year]['Unsold Shares'] = total_grant_shares - results[year]['Cumulative Redeemed']
        
        # Redemption value = (share price - strike price) * redeemed shares
        share_price_diff = max(0, results[year]['Share Price'] - strike_price)
        results[year]['Redemption Value'] = share_price_diff * results[year]['Redeemed Shares']
        
        # Cumulative redemption value
        results[year]['Cumulative Redemption Value'] = results[year-1]['Cumulative Redemption Value'] + results[year]['Redemption Value']
        
        # Value of unsold shares
        results[year]['Value of Unsold Shares'] = share_price_diff * results[year]['Unsold Shares']
        
        # Total grant value = cumulative redemption value + value of unsold shares
        results[year]['Total Grant Value'] = results[year]['Cumulative Redemption Value'] + results[year]['Value of Unsold Shares']
    
    # Calculate combined values
    for year in range(2025, 2036):
        results[year]['Combined Total Value'] = results[year]['Total Common Share Value'] + results[year]['Total Grant Value']
    
    return results

# Check if we should apply the same rate to both common and options
same_rates = st.sidebar.checkbox("Use same redemption rate for both Common Shares and Options", value=True)

try:
    # Calculate results based on redemption rates
    if same_rates:
        # Use common redemption rate for both
        results = calculate_results(common_redemption_rate, common_redemption_rate)
    else:
        # Use separate rates
        results = calculate_results(common_redemption_rate, option_redemption_rate)
except Exception as e:
    st.error(f"An error occurred during calculations: {str(e)}")
    # Provide fallback calculation with 0% rates
    results = calculate_results(0.0, 0.0)

# Create tabs for the three main sections
tab1, tab2, tab3 = st.tabs(["Common Share Analysis", "A-Share/Options Analysis", "Combined Analysis"])

# Tab 1: Common Shares Results and Chart
with tab1:
    st.header("Common Share Grant Value")
    st.markdown(f"**Common Share Redemption Rate: {int(common_redemption_rate*100)}%, PBT Growth: {int(pbt_growth_rate*100)}%**")
    
    # Common Shares Summary Table
    common_years = list(range(2025, 2036))  # Start from 2025 as requested
    common_data = {
        "Year": common_years,
        "Share Price (£)": [f"£{results[year]['Share Price']:.2f}" for year in common_years],
        "Proceeds from Redemption (£)": [f"£{results[year]['Cumulative Common Redemption Value']:,.2f}" for year in common_years],
        "Value of Unsold Shares (£)": [f"£{results[year]['Value of Unsold Common Shares']:,.2f}" for year in common_years],
        "Total Common Share Value (£)": [f"£{results[year]['Total Common Share Value']:,.2f}" for year in common_years]
    }
    common_df = pd.DataFrame(common_data)
    st.dataframe(common_df, use_container_width=True, hide_index=True)
    
    # Common Share Chart
    try:
        st.subheader("Common Share Grant Value (£ thousands)")
        
        # Convert to thousands for y-axis
        chart_years = list(range(2026, 2036))  # X-axis: 2026 to 2035 as requested
        chart_common_data = pd.DataFrame({
            "Year": chart_years,
            "Proceeds from Redemption": [results[year]['Cumulative Common Redemption Value']/1000 for year in chart_years],
            "Value of Unsold Shares": [results[year]['Value of Unsold Common Shares']/1000 for year in chart_years],
            "Total Value": [results[year]['Total Common Share Value']/1000 for year in chart_years]
        })
        
        # Set Year as index for the chart
        chart_common_data = chart_common_data.set_index("Year")
        
        # Display the chart
        st.line_chart(chart_common_data, height=400)
        st.caption(f"Fixed parameters: PBT Growth Rate: {int(pbt_growth_rate*100)}%, Common Share Redemption: {int(common_redemption_rate*100)}%")
    except Exception as e:
        st.error(f"Error creating Common Share chart: {str(e)}")

# Tab 2: A-Share/Options Results and Chart
with tab2:
    st.header("A-Share/Options Grant Value")
    st.markdown(f"**A-Share/Options Redemption Rate: {int(option_redemption_rate*100)}%, PBT Growth: {int(pbt_growth_rate*100)}%**")
    
    # A-Share/Options Summary Table
    options_data = {
        "Year": common_years,
        "Share Price (£)": [f"£{results[year]['Share Price']:.2f}" for year in common_years],
        "Proceeds from Redemption (£)": [f"£{results[year]['Cumulative Redemption Value']:,.2f}" for year in common_years],
        "Value of Unsold Shares (£)": [f"£{results[year]['Value of Unsold Shares']:,.2f}" for year in common_years],
        "Total A-Share/Options Value (£)": [f"£{results[year]['Total Grant Value']:,.2f}" for year in common_years]
    }
    options_df = pd.DataFrame(options_data)
    st.dataframe(options_df, use_container_width=True, hide_index=True)
    
    # A-Share/Options Chart
    try:
        st.subheader("A-Share/Options Grant Value (£ thousands)")
        
        # Convert to thousands for y-axis
        chart_years = list(range(2026, 2036))
        chart_options_data = pd.DataFrame({
            "Year": chart_years,
            "Proceeds from Redemption": [results[year]['Cumulative Redemption Value']/1000 for year in chart_years],
            "Value of Unsold Shares": [results[year]['Value of Unsold Shares']/1000 for year in chart_years],
            "Total Value": [results[year]['Total Grant Value']/1000 for year in chart_years]
        })
        
        # Set Year as index for the chart
        chart_options_data = chart_options_data.set_index("Year")
        
        # Display the chart
        st.line_chart(chart_options_data, height=400)
        st.caption(f"Fixed parameters: PBT Growth Rate: {int(pbt_growth_rate*100)}%, A-Share/Options Redemption: {int(option_redemption_rate*100)}%")
    except Exception as e:
        st.error(f"Error creating A-Share/Options chart: {str(e)}")

# Tab 3: Combined Results and PBT Growth Comparison Chart
with tab3:
    st.header("Combined Grant Value")
    redemption_label = f"{int(common_redemption_rate*100)}% Redemption" if same_rates else f"Common: {int(common_redemption_rate*100)}%, Options: {int(option_redemption_rate*100)}%"
    st.markdown(f"**Redemption Rates: {redemption_label}, PBT Growth: {int(pbt_growth_rate*100)}%**")
    
    # Combined Summary Table
    combined_data = {
        "Year": common_years,
        "Share Price (£)": [f"£{results[year]['Share Price']:.2f}" for year in common_years],
        "Common Share Value (£)": [f"£{results[year]['Total Common Share Value']:,.2f}" for year in common_years],
        "A-Share/Options Value (£)": [f"£{results[year]['Total Grant Value']:,.2f}" for year in common_years],
        "Combined Total Value (£)": [f"£{results[year]['Combined Total Value']:,.2f}" for year in common_years]
    }
    combined_df = pd.DataFrame(combined_data)
    st.dataframe(combined_df, use_container_width=True, hide_index=True)
    
    # Combined Value Chart
    try:
        st.subheader("Combined Grant Value (£ thousands)")
        
        # Convert to thousands for y-axis
        chart_years = list(range(2026, 2036))
        chart_combined_data = pd.DataFrame({
            "Year": chart_years,
            "Common Share Value": [results[year]['Total Common Share Value']/1000 for year in chart_years],
            "A-Share/Options Value": [results[year]['Total Grant Value']/1000 for year in chart_years],
            "Combined Total Value": [results[year]['Combined Total Value']/1000 for year in chart_years]
        })
        
        # Set Year as index for the chart
        chart_combined_data = chart_combined_data.set_index("Year")
        
        # Display the chart
        st.line_chart(chart_combined_data, height=400)
        st.caption(f"Fixed parameters: PBT Growth Rate: {int(pbt_growth_rate*100)}%, Redemptions: {redemption_label}")
    except Exception as e:
        st.error(f"Error creating Combined Values chart: {str(e)}")
    
    # PBT Growth Comparison Chart
    st.subheader("Effect of Different PBT Growth Rates on Combined Value")
    
    # Create comparison data with different PBT growth rates
    try:
        # Define growth rates to compare
        growth_rates = [0.10, 0.15, 0.20, 0.25]
        chart_years = list(range(2026, 2036))
        
        # Create DataFrame for chart
        growth_chart_data = {}
        
        # Calculate for each growth rate
        for rate in growth_rates:
            # Create a temporary function for this growth rate calculation
            def calc_with_rate(growth_rate):
                # Calculate share price series with this growth rate
                prices = [6.00]  # Start with 2024 base price
                for i in range(1, 12):  # 2025-2035
                    prices.append(prices[-1] * (1 + growth_rate))
                
                # For 2026-2035 (chart years)
                combined_values = []
                for idx, year in enumerate(chart_years):
                    # Current price (2026 is index 2 in prices)
                    price = prices[idx + 2]
                    
                    # Common share value (simplified calculation)
                    common_price_diff = max(0, price - common_purchase_price)
                    common_value = common_price_diff * total_common_shares
                    
                    # A-Share/Options value (simplified calculation)
                    option_price_diff = max(0, price - strike_price)
                    option_value = option_price_diff * total_grant_shares
                    
                    # Combined value
                    combined_values.append((common_value + option_value) / 1000)  # Convert to thousands
                
                return combined_values
            
            # Store result for this growth rate
            label = f"{int(rate*100)}% Growth"
            growth_chart_data[label] = calc_with_rate(rate)
        
        # Create DataFrame and set index to years
        growth_df = pd.DataFrame(growth_chart_data, index=chart_years)
        
        # Display chart
        st.line_chart(growth_df, height=400)
        st.caption(f"Fixed parameters: Common Redemption: {int(common_redemption_rate*100)}%, Options Redemption: {int(option_redemption_rate*100)}%")
        st.info("Note: This comparison uses a simplified calculation that assumes no redemptions to show growth rate effect.")
    
    except Exception as e:
        st.error(f"Error creating PBT Growth comparison chart: {str(e)}")
        st.info("Unable to generate PBT Growth comparison chart. Please check your parameters.")

# Download button for all results
try:
    # Prepare download data with all years
    download_years = list(range(2025, 2036))
    
    download_data = {
        "Year": download_years,
        "Share Price (£)": [results[year]['Share Price'] for year in download_years],
        "Common Redemption Value (£)": [results[year]['Cumulative Common Redemption Value'] for year in download_years],
        "Common Unsold Value (£)": [results[year]['Value of Unsold Common Shares'] for year in download_years],
        "Total Common Value (£)": [results[year]['Total Common Share Value'] for year in download_years],
        "Options Redemption Value (£)": [results[year]['Cumulative Redemption Value'] for year in download_years],
        "Options Unsold Value (£)": [results[year]['Value of Unsold Shares'] for year in download_years],
        "Total Options Value (£)": [results[year]['Total Grant Value'] for year in download_years],
        "Combined Total Value (£)": [results[year]['Combined Total Value'] for year in download_years]
    }
    
    download_df = pd.DataFrame(download_data)
    csv = download_df.to_csv(index=False)
    
    st.download_button(
        label=f"Download Complete Results as CSV",
        data=csv,
        file_name=f"oaknorth_grants_pbt_{int(pbt_growth_rate*100)}_common_{int(common_redemption_rate*100)}_options_{int(option_redemption_rate*100)}.csv",
        mime="text/csv",
    )
except Exception as e:
    st.error(f"Error preparing download data: {str(e)}")
    st.info("Unable to generate download file. Please check your parameters and try again.")

# Add a footer
st.markdown("---")
st.caption("OakNorth Grants Analysis Tool © 2025")
