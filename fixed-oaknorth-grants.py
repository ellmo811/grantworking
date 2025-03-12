import streamlit as st
import pandas as pd
import numpy as np

# Set page config first before any other Streamlit commands
st.set_page_config(
    page_title="OakNorth Grants Working Sheet",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display the main title
st.title("OakNorth Grants Working Sheet")
st.markdown("This working sheet allows you to analyze the impact of different growth and share redemption rates on OakNorth grants value.")

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
    min_value=0,
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
vested_shares_input = {}

# Set default values for all years
default_values = {
    2025: 60000,
    2026: 70000,
    2027: 80000,
    2028: 90000,
    2029: 100000
}

# Fill default values for all years
for year in years_range:
    if year in default_values:
        vested_shares_input[year] = default_values[year]
    else:
        vested_shares_input[year] = 100000  # All years after 2029 are fully vested

if vesting_method == "Default Schedule":
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
            default_value = default_values.get(year, 100000)  # Use the default values dictionary
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

    # Validation check to ensure vested shares are non-decreasing
    sorted_years = sorted(vested_shares_input.keys())
    for i in range(1, len(sorted_years)):
        if vested_shares_input[sorted_years[i]] < vested_shares_input[sorted_years[i-1]]:
            st.sidebar.warning(f"Warning: Vested shares for year {sorted_years[i]} are less than previous year. Vesting should typically be non-decreasing.")

# Function to calculate results for specific redemption rates
def calculate_results(growth_rate=None):
    # Use the provided growth rate or default to the global pbt_growth_rate
    if growth_rate is None:
        growth_rate = pbt_growth_rate
        
    years = list(range(2024, 2036))
    results = {}
    
    # Initialize objects for all years
    for year in years:
        results[year] = {}
    
    # Calculate share price series
    results[2024]['Share Price'] = 6.00  # Base price in 2024
    for year in range(2025, 2036):
        results[year]['Share Price'] = results[year-1]['Share Price'] * (1 + growth_rate)
    
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
    # Safely get vested shares for 2025 with a default of 0 if not found
    vested_2025 = vested_shares_input.get(2025, 0)
    results[2025]['Vested Shares'] = vested_2025
    results[2025]['Redeemed Shares'] = 0
    results[2025]['Cumulative Redeemed'] = 0
    results[2025]['Vested Unsold Shares'] = results[2025]['Vested Shares']
    results[2025]['Unsold Shares'] = total_grant_shares
    results[2025]['Redemption Value'] = 0
    results[2025]['Cumulative Redemption Value'] = 0
    
    # Calculate value of unsold shares for 2025
    share_price_diff_2025 = max(0, results[2025]['Share Price'] - strike_price)
    results[2025]['Value of Unsold Shares'] = share_price_diff_2025 * results[2025]['Vested Shares']  # Only count vested shares
    results[2025]['Total Grant Value'] = results[2025]['Value of Unsold Shares']
    
    # Calculate option values for 2026-2035
    for year in range(2026, 2036):
        # Vested shares for this year from input (safely with a default)
        vested_shares = vested_shares_input.get(year, vested_shares_input.get(year-1, 0))
        results[year]['Vested Shares'] = vested_shares
        
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
        
        # Value of unsold shares (only count vested ones)
        results[year]['Value of Unsold Shares'] = share_price_diff * results[year]['Vested Unsold Shares']
        
        # Total grant value = cumulative redemption value + value of unsold shares
        results[year]['Total Grant Value'] = results[year]['Cumulative Redemption Value'] + results[year]['Value of Unsold Shares']
    
    # Calculate combined values
    for year in range(2025, 2036):
        results[year]['Combined Total Value'] = results[year]['Total Common Share Value'] + results[year]['Total Grant Value']
    
    return results

# Try to calculate results and handle any errors
try:
    # Calculate results 
    results = calculate_results()
except Exception as e:
    st.error(f"An error occurred during calculations: {str(e)}")
    # Provide fallback calculation with 0% rates
    try:
        st.warning("Attempting fallback calculation with default values.")
        # Use fixed default values
        pbt_growth_rate = 0.20
        common_redemption_rate = 0.05
        option_redemption_rate = 0.05
        results = calculate_results()
    except Exception as e2:
        st.error(f"Fallback calculation also failed: {str(e2)}")
        st.stop()  # Stop execution if fallback also fails

# Create tabs based on whether common shares exist
if total_common_shares > 0:
    tab1, tab2, tab3 = st.tabs(["Common Share Analysis", "A-Share/Options Analysis", "Combined Analysis"])
else:
    # Only show options tab if no common shares
    tab2 = st.container()  # Use a container instead of tabs
    st.info("Common Share Analysis and Combined Analysis tabs are hidden because Total Common Shares is set to 0.")

# Tab 1: Common Shares Results and Sensitivity Chart
if total_common_shares > 0:
    with tab1:
        st.header("Common Share Grant Value")
        st.markdown(f"**Common Share Redemption Rate: {int(common_redemption_rate*100)}%, PBT Growth: {int(pbt_growth_rate*100)}%**")
        
        # Common Shares Summary Table
        common_years = list(range(2025, 2036))  # Start from 2025 as requested
        common_data = {
            "Year": common_years,
            "Share Price (£)": [f"£{results[year]['Share Price']:.0f}" for year in common_years],
            "Proceeds from Redemption (£)": [f"£{results[year]['Cumulative Common Redemption Value']:,.0f}" for year in common_years],
            "Value of Unsold Shares (£)": [f"£{results[year]['Value of Unsold Common Shares']:,.0f}" for year in common_years],
            "Total Common Share Value (£)": [f"£{results[year]['Total Common Share Value']:,.0f}" for year in common_years]
        }
        common_df = pd.DataFrame(common_data)
        st.dataframe(common_df, use_container_width=True, hide_index=True)
        
        # Common Share Sensitivity Chart explanation
        st.subheader("Common Share Value Sensitivity")
        st.write("This section shows how the total value of common shares changes with different redemption rates.")

# Tab 2: Options Results
with tab2:
    st.header("A-Share/Options Grant Value")
    st.markdown(f"**A-Share/Options Redemption Rate: {int(option_redemption_rate*100)}%, PBT Growth: {int(pbt_growth_rate*100)}%**")
    
    # Display vesting schedule used in calculations
    vesting_data = {
        "Year": list(vested_shares_input.keys()),
        "Vested Shares": list(vested_shares_input.values())
    }
    st.subheader("Vesting Schedule Used")
    vesting_df = pd.DataFrame(vesting_data)
    st.dataframe(vesting_df, use_container_width=True, hide_index=True)
    
    # Options Summary Table
    option_years = list(range(2025, 2036))
    option_data = {
        "Year": option_years,
        "Share Price (£)": [f"£{results[year]['Share Price']:.0f}" for year in option_years],
        "Vested Shares": [f"{results[year]['Vested Shares']:,.0f}" for year in option_years],
        "Vested Unsold Shares": [f"{results[year]['Vested Unsold Shares']:,.0f}" for year in option_years],
        "Proceeds from Redemption (£)": [f"£{results[year]['Cumulative Redemption Value']:,.0f}" for year in option_years],
        "Value of Unsold Shares (£)": [f"£{results[year]['Value of Unsold Shares']:,.0f}" for year in option_years],
        "Total Grant Value (£)": [f"£{results[year]['Total Grant Value']:,.0f}" for year in option_years]
    }
    option_df = pd.DataFrame(option_data)
    st.dataframe(option_df, use_container_width=True, hide_index=True)

# Tab 3: Combined Analysis
if total_common_shares > 0:
    with tab3:
        st.header("Combined Analysis")
        st.markdown(f"**Common Share Redemption Rate: {int(common_redemption_rate*100)}%, A-Share/Options Redemption Rate: {int(option_redemption_rate*100)}%, PBT Growth: {int(pbt_growth_rate*100)}%**")
        
        # Combined Summary Table
        combined_years = list(range(2025, 2036))
        combined_data = {
            "Year": combined_years,
            "Share Price (£)": [f"£{results[year]['Share Price']:.0f}" for year in combined_years],
            "Common Share Value (£)": [f"£{results[year]['Total Common Share Value']:,.0f}" for year in combined_years],
            "A-Share/Options Value (£)": [f"£{results[year]['Total Grant Value']:,.0f}" for year in combined_years],
            "Combined Total Value (£)": [f"£{results[year]['Combined Total Value']:,.0f}" for year in combined_years]
        }
        combined_df = pd.DataFrame(combined_data)
        st.dataframe(combined_df, use_container_width=True, hide_index=True)
