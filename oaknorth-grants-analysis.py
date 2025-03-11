import streamlit as st
import pandas as pd
import numpy as np

# Note: matplotlib.pyplot is imported but not used in the app
# Import only if you need to create custom plots outside of st.line_chart
# import matplotlib.pyplot as plt

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

# Common share redemption percentage
common_redemption_rates = st.sidebar.multiselect(
    "Common Share Redemption Percentages", 
    options=[0, 3, 5, 8, 10],
    default=[0, 3, 5, 8, 10],
    help="Percentages of common shares to redeem each year starting from 2026"
)
# Ensure we have at least one rate selected
if not common_redemption_rates:
    st.sidebar.warning("No common redemption rates selected. Using 0% as default.")
    common_redemption_rates = [0]
# Convert to float values
common_redemption_rates = [rate / 100 for rate in common_redemption_rates]

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

# Options redemption percentages
option_redemption_rates = st.sidebar.multiselect(
    "A-Share/Options Redemption Percentages", 
    options=[0, 3, 5, 8, 10],
    default=[0, 3, 5, 8, 10],
    help="Percentages of vested unsold A-Share/Options to redeem each year"
)
# Ensure we have at least one rate selected
if not option_redemption_rates:
    st.sidebar.warning("No option redemption rates selected. Using 0% as default.")
    option_redemption_rates = [0]
# Convert to float values
option_redemption_rates = [rate / 100 for rate in option_redemption_rates]

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

# Generate results for all combinations of redemption rates
all_results = {}

# Check if we should apply the same rate to both common and options
same_rates = st.sidebar.checkbox("Use same redemption rate for both Common Shares and Options", value=True)

try:
    if same_rates:
        # Use the common redemption rates for both
        for rate in common_redemption_rates:
            rate_key = f"{int(rate*100)}%"
            all_results[rate_key] = calculate_results(rate, rate)
    else:
        # Generate all combinations
        for c_rate in common_redemption_rates:
            for o_rate in option_redemption_rates:
                rate_key = f"Common {int(c_rate*100)}% / Options {int(o_rate*100)}%"
                all_results[rate_key] = calculate_results(c_rate, o_rate)
                
    # Make sure we have at least one result
    if not all_results:
        st.warning("No calculation results. Using 0% redemption rate as default.")
        all_results["0%"] = calculate_results(0.0, 0.0)
except Exception as e:
    st.error(f"An error occurred during calculations: {str(e)}")
    # Provide a fallback calculation
    all_results["0%"] = calculate_results(0.0, 0.0)

# Create tabs for different views
try:
    tab1, tab2, tab3, tab4 = st.tabs(["Common Share Values", "A-Share/Options Values", "Combined Values", "Charts"])
except Exception as e:
    st.error(f"Error creating tabs: {str(e)}")
    st.warning("Displaying results in sequential order instead of tabs")
    # Create placeholders for our content instead
    tab1 = tab2 = tab3 = tab4 = st

with tab1:
    st.header("Common Share Grant Value at Various Redemption Rates")
    
    # Create a DataFrame for Common Share values
    common_years = list(range(2026, 2036))
    common_data = {}
    
    # Add Share Price column
    try:
        first_key = list(all_results.keys())[0]  # Any rate will do for share price
        common_data["Share Price (£)"] = [f"£{all_results[first_key][year]['Share Price']:.2f}" for year in common_years]
    except (IndexError, KeyError) as e:
        st.error(f"Error getting share prices: {str(e)}")
        common_data["Share Price (£)"] = ["N/A"] * len(common_years)
    
    # Add value columns for each redemption rate
    for rate_key in all_results.keys():
        common_data[f"{rate_key} Value (£)"] = [f"£{all_results[rate_key][year]['Total Common Share Value']:,.2f}" 
                                                for year in common_years]
    
    common_df = pd.DataFrame(common_data, index=common_years)
    common_df.index.name = "Year"
    
    st.dataframe(common_df, use_container_width=True)

with tab2:
    st.header("A-Share/Options Grant Value at Various Redemption Rates")
    
    # Create a DataFrame for A-Share/Options values
    options_years = list(range(2026, 2036))
    options_data = {}
    
    # Add Share Price column
    options_data["Share Price (£)"] = [f"£{all_results[first_key][year]['Share Price']:.2f}" for year in options_years]
    
    # Add value columns for each redemption rate
    for rate_key in all_results.keys():
        options_data[f"{rate_key} Value (£)"] = [f"£{all_results[rate_key][year]['Total Grant Value']:,.2f}" 
                                                 for year in options_years]
    
    options_df = pd.DataFrame(options_data, index=options_years)
    options_df.index.name = "Year"
    
    st.dataframe(options_df, use_container_width=True)

with tab3:
    st.header("Combined Grant Value at Various Redemption Rates")
    
    # Create a DataFrame for Combined values
    combined_years = list(range(2026, 2036))
    combined_data = {}
    
    # Add Share Price column
    combined_data["Share Price (£)"] = [f"£{all_results[first_key][year]['Share Price']:.2f}" for year in combined_years]
    
    # Add value columns for each redemption rate
    for rate_key in all_results.keys():
        combined_data[f"{rate_key} Value (£)"] = [f"£{all_results[rate_key][year]['Combined Total Value']:,.2f}" 
                                                  for year in combined_years]
    
    combined_df = pd.DataFrame(combined_data, index=combined_years)
    combined_df.index.name = "Year"
    
    st.dataframe(combined_df, use_container_width=True)

with tab4:
    st.header("Grant Value Visualizations")
    
    # Create chart for Common Share values
    st.subheader("Common Share Grant Value")
    
    try:
        chart_common_years = list(range(2026, 2036))
        chart_common_data = pd.DataFrame(index=chart_common_years)
        
        for rate_key in all_results.keys():
            chart_common_data[rate_key] = [all_results[rate_key][year]['Total Common Share Value'] for year in chart_common_years]
        
        st.line_chart(chart_common_data)
    except Exception as e:
        st.error(f"Error creating Common Share chart: {str(e)}")
        st.info("Please check your input parameters and try again.")
    
    # Create chart for A-Share/Options values
    st.subheader("A-Share/Options Grant Value")
    
    try:
        chart_options_years = list(range(2026, 2036))
        chart_options_data = pd.DataFrame(index=chart_options_years)
        
        for rate_key in all_results.keys():
            chart_options_data[rate_key] = [all_results[rate_key][year]['Total Grant Value'] for year in chart_options_years]
        
        st.line_chart(chart_options_data)
    except Exception as e:
        st.error(f"Error creating A-Share/Options chart: {str(e)}")
        st.info("Please check your input parameters and try again.")
    
    # Create chart for Combined values
    st.subheader("Combined Grant Value")
    
    try:
        chart_combined_years = list(range(2026, 2036))
        chart_combined_data = pd.DataFrame(index=chart_combined_years)
        
        for rate_key in all_results.keys():
            chart_combined_data[rate_key] = [all_results[rate_key][year]['Combined Total Value'] for year in chart_combined_years]
        
        st.line_chart(chart_combined_data)
    except Exception as e:
        st.error(f"Error creating Combined Values chart: {str(e)}")
        st.info("Please check your input parameters and try again.")

# Download button for results
try:
    year_to_download = st.selectbox("Select year to download data for:", range(2026, 2036))
    
    download_data = {
        "Redemption Rate": [],
        "Share Price (£)": [],
        "Common Share Value (£)": [],
        "A-Share/Options Value (£)": [],
        "Combined Value (£)": []
    }
    
    for rate_key in all_results.keys():
        download_data["Redemption Rate"].append(rate_key)
        download_data["Share Price (£)"].append(all_results[rate_key][year_to_download]['Share Price'])
        download_data["Common Share Value (£)"].append(all_results[rate_key][year_to_download]['Total Common Share Value'])
        download_data["A-Share/Options Value (£)"].append(all_results[rate_key][year_to_download]['Total Grant Value'])
        download_data["Combined Value (£)"].append(all_results[rate_key][year_to_download]['Combined Total Value'])
    
    download_df = pd.DataFrame(download_data)
    csv = download_df.to_csv(index=False)
    
    st.download_button(
        label=f"Download {year_to_download} results as CSV",
        data=csv,
        file_name=f"oaknorth_grants_{year_to_download}.csv",
        mime="text/csv",
    )
except Exception as e:
    st.error(f"Error preparing download data: {str(e)}")
    st.info("Unable to generate download file. Please check your parameters and try again.")

# Add a footer
st.markdown("---")
st.caption("OakNorth Grants Analysis Tool © 2025")
