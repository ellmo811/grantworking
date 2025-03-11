import streamlit as st
import pandas as pd
import numpy as np

# Set page title and configuration
st.set_page_config(page_title="OakNorth Grants Working Sheet", layout="wide")
st.title("OakNorth Grants Working Sheet")

# Sidebar for inputs - reorganized as requested
st.sidebar.header("Input Parameters")

# PBT Growth Rate at the top
pbt_growth_rate = st.sidebar.slider(
    "PBT Growth Rate", 
    min_value=0, 
    max_value=20,
    value=15,
    step=1,
    help="Annual growth rate of share price"
) / 100

# Common Share section first
st.sidebar.header("Common Share")

# Common share redemption percentage
common_redemption_percentage = st.sidebar.slider(
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
    value=10000,
    step=100,
    help="Total number of common shares"
)

# Get common share purchase price
common_purchase_price = st.sidebar.number_input(
    "Common Share Purchase Price (£)",
    min_value=0.01,
    value=2.00,
    step=0.01,
    format="%.2f",
    help="Initial purchase price of common shares"
)

# A-Share / Options section second
st.sidebar.header("A-Share / Options")

# Get redemption percentage for A-shares/options
redemption_percentage = st.sidebar.slider(
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
    value=10000,
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
        2025: 6000,
        2026: 7000,
        2027: 8000,
        2028: 9000,
        2029: 10000
    }
    # Fill in the dictionary with default values
    for year in years_range:
        if year in default_values:
            vested_shares_input[year] = default_values[year]
        else:
            vested_shares_input[year] = 10000  # All years after 2029 are fully vested
    
    # Display the default schedule
    st.sidebar.write("Default vesting schedule:")
    default_schedule = pd.DataFrame({
        "Year": vested_shares_input.keys(), 
        "Vested Shares": vested_shares_input.values()
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
            default_value = 6000 if year == 2025 else 7000 if year == 2026 else 8000 if year == 2027 else 9000 if year == 2028 else 10000
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
                value=10000, 
                step=100,
                key=f"vest_{year}"
            )

# Calculate values with specific redemption and growth rates WITHOUT ANY ROUNDING
def calculate_values(redemption_pct, growth_pct, vesting_input, common_redemption_pct, common_shares, common_price):
    """
    Calculate equity values over time based on given parameters
    
    Parameters:
    - redemption_pct: Percentage of vested unsold A-Share/Options to redeem each year
    - growth_pct: Annual growth rate of share price
    - vesting_input: Dictionary with years as keys and vested shares as values
    - common_redemption_pct: Percentage of common shares to redeem each year
    - common_shares: Total number of common shares
    - common_price: Purchase price of common shares
    
    Returns:
    - DataFrame with calculated values for each year
    """
    # Initialize dataframe for years 2024-2035
    years = list(range(2024, 2036))
    df = pd.DataFrame(index=years)
    
    # Initialize all columns with zeros to ensure consistency
    columns = [
        # Option shares columns
        'Share Price', 'Vested Shares', 'Vested Unsold Shares', 'Redeemed Shares',
        'Cumulative Redeemed', 'Unsold Shares', 'Redemption Value',
        'Cumulative Redemption Value', 'Value of Unsold Shares', 'Total Grant Value',
        # Common shares columns
        'Common Shares Redeemed', 'Cumulative Common Redeemed', 'Unsold Common Shares',
        'Common Redemption Value', 'Cumulative Common Redemption Value',
        'Value of Unsold Common Shares', 'Total Common Share Value',
        # Combined total value
        'Combined Total Value'
    ]
    
    for col in columns:
        df[col] = 0.0
    
    # Initial values for 2024
    df.loc[2024, 'Share Price'] = strike_price
    df.loc[2024, 'Unsold Shares'] = total_grant_shares
    df.loc[2024, 'Unsold Common Shares'] = common_shares
    
    # Year 2025 calculations (no redemption in first year)
    df.loc[2025, 'Share Price'] = df.loc[2024, 'Share Price'] * (1 + growth_pct)
    df.loc[2025, 'Vested Shares'] = vesting_input[2025]
    df.loc[2025, 'Vested Unsold Shares'] = df.loc[2025, 'Vested Shares']
    df.loc[2025, 'Unsold Shares'] = total_grant_shares
    
    # A-Shares/Options 2025 value calculation
    share_price_diff = max(0, df.loc[2025, 'Share Price'] - strike_price)
    df.loc[2025, 'Value of Unsold Shares'] = share_price_diff * df.loc[2025, 'Unsold Shares']
    df.loc[2025, 'Total Grant Value'] = df.loc[2025, 'Value of Unsold Shares']
    
    # Common shares 2025 value calculation
    df.loc[2025, 'Unsold Common Shares'] = common_shares
    common_price_diff = max(0, df.loc[2025, 'Share Price'] - common_price)
    df.loc[2025, 'Value of Unsold Common Shares'] = common_price_diff * df.loc[2025, 'Unsold Common Shares']
    df.loc[2025, 'Total Common Share Value'] = df.loc[2025, 'Value of Unsold Common Shares']
    
    # Combined total for 2025
    df.loc[2025, 'Combined Total Value'] = df.loc[2025, 'Total Grant Value'] + df.loc[2025, 'Total Common Share Value']
    
    # Calculate for years 2026-2035
    for year in range(2026, 2036):
        # Share price calculation: previous price * (1 + growth rate)
        df.loc[year, 'Share Price'] = df.loc[year-1, 'Share Price'] * (1 + growth_pct)
        
        # Option Shares Calculations
        # Vested shares from input
        df.loc[year, 'Vested Shares'] = vesting_input[year]
        
        # Redeemed shares for this year - based on PREVIOUS year's VESTED UNSOLD SHARES
        df.loc[year, 'Redeemed Shares'] = df.loc[year-1, 'Vested Unsold Shares'] * redemption_pct
        
        # Update cumulative redeemed
        df.loc[year, 'Cumulative Redeemed'] = df.loc[year-1, 'Cumulative Redeemed'] + df.loc[year, 'Redeemed Shares']
        
        # Vested unsold shares = vested shares - cumulative redeemed
        df.loc[year, 'Vested Unsold Shares'] = max(0, df.loc[year, 'Vested Shares'] - df.loc[year, 'Cumulative Redeemed'])
        
        # Unsold shares = total shares minus cumulative redeemed
        df.loc[year, 'Unsold Shares'] = total_grant_shares - df.loc[year, 'Cumulative Redeemed']
        
        # Redemption value = (share price - strike price) * redeemed shares
        share_price_diff = max(0, df.loc[year, 'Share Price'] - strike_price)
        df.loc[year, 'Redemption Value'] = share_price_diff * df.loc[year, 'Redeemed Shares']
        
        # Cumulative redemption value
        df.loc[year, 'Cumulative Redemption Value'] = df.loc[year-1, 'Cumulative Redemption Value'] + df.loc[year, 'Redemption Value']
        
        # Value of unsold shares = (share price - strike price) * unsold shares
        df.loc[year, 'Value of Unsold Shares'] = share_price_diff * df.loc[year, 'Unsold Shares']
        
        # Total grant value = cumulative redemption value + value of unsold shares
        df.loc[year, 'Total Grant Value'] = df.loc[year, 'Cumulative Redemption Value'] + df.loc[year, 'Value of Unsold Shares']
        
        # Common Shares Calculations - redemption starts in 2026
        # Common shares redeemed (% of previous year's unsold common shares)
        df.loc[year, 'Common Shares Redeemed'] = df.loc[year-1, 'Unsold Common Shares'] * common_redemption_pct
        
        # Cumulative common shares redeemed
        df.loc[year, 'Cumulative Common Redeemed'] = df.loc[year-1, 'Cumulative Common Redeemed'] + df.loc[year, 'Common Shares Redeemed']
        
        # Unsold common shares
        df.loc[year, 'Unsold Common Shares'] = common_shares - df.loc[year, 'Cumulative Common Redeemed']
        
        # Common redemption value = (share price - common purchase price) * common shares redeemed
        common_price_diff = max(0, df.loc[year, 'Share Price'] - common_price)
        df.loc[year, 'Common Redemption Value'] = common_price_diff * df.loc[year, 'Common Shares Redeemed']
        
        # Cumulative common redemption value
        df.loc[year, 'Cumulative Common Redemption Value'] = df.loc[year-1, 'Cumulative Common Redemption Value'] + df.loc[year, 'Common Redemption Value']
        
        # Value of unsold common shares
        df.loc[year, 'Value of Unsold Common Shares'] = common_price_diff * df.loc[year, 'Unsold Common Shares']
        
        # Total common share value
        df.loc[year, 'Total Common Share Value'] = df.loc[year, 'Cumulative Common Redemption Value'] + df.loc[year, 'Value of Unsold Common Shares']
        
        # Combined total value
        df.loc[year, 'Combined Total Value'] = df.loc[year, 'Total Grant Value'] + df.loc[year, 'Total Common Share Value']
    
    return df

# Try-except block for error handling
try:
    # Main results with user-selected parameters
    results = calculate_values(
        redemption_percentage, 
        pbt_growth_rate, 
        vested_shares_input, 
        common_redemption_percentage,
        total_common_shares,
        common_purchase_price
    )
    
    # Display Common Share results table first as requested
    st.write("### Common Share Grant Value")
    filtered_common_results = results.loc[2025:, ['Share Price', 'Cumulative Common Redemption Value', 'Total Common Share Value']]
    filtered_common_results = filtered_common_results.rename(columns={
        'Share Price': 'Share Repurchase Price (£)',
        'Cumulative Common Redemption Value': 'Proceeds from Common Share Redemption (£)',
        'Total Common Share Value': 'Total Common Share Value (£)'
    })
    
    # Format for display
    display_common_df = filtered_common_results.copy()
    
    # Format indices as strings ('2025', '2026', etc.)
    display_common_df.index = display_common_df.index.map(lambda x: f'{x}')
    
    # Format share price with 2 decimal places
    display_common_df['Share Repurchase Price (£)'] = display_common_df['Share Repurchase Price (£)'].apply(lambda x: f"£{x:.2f}")
    
    # Format other columns with NO decimal places, only thousands separator
    for col in ['Proceeds from Common Share Redemption (£)', 'Total Common Share Value (£)']:
        display_common_df[col] = display_common_df[col].apply(lambda x: f"£{int(x):,}")
    
    # Display the common share summary table
    st.dataframe(display_common_df, use_container_width=True)
    
    # Display A-Share/Options results table next
    st.write("### A-Share/Options Grant Value")
    filtered_option_results = results.loc[2025:, ['Share Price', 'Cumulative Redemption Value', 'Total Grant Value']]
    filtered_option_results = filtered_option_results.rename(columns={
        'Share Price': 'Share Repurchase Price (£)',
        'Cumulative Redemption Value': 'Proceeds from A-Share/Options Redemption (£)',
        'Total Grant Value': 'Total A-Share/Options Value (£)'
    })
    
    # Format for display
    display_option_df = filtered_option_results.copy()
    
    # Format indices as strings ('2025', '2026', etc.)
    display_option_df.index = display_option_df.index.map(lambda x: f'{x}')
    
    # Format share price with 2 decimal places
    display_option_df['Share Repurchase Price (£)'] = display_option_df['Share Repurchase Price (£)'].apply(lambda x: f"£{x:.2f}")
    
    # Format other columns with NO decimal places, only thousands separator
    for col in ['Proceeds from A-Share/Options Redemption (£)', 'Total A-Share/Options Value (£)']:
        display_option_df[col] = display_option_df[col].apply(lambda x: f"£{int(x):,}")
    
    # Display the option summary table
    st.dataframe(display_option_df, use_container_width=True)
    
    # Display Combined Total Value table
    st.write("### Combined Grants Value")
    
    # Filter to only show 2025 onwards and the combined value
    filtered_combined_results = results.loc[2025:, ['Combined Total Value']]
    filtered_combined_results = filtered_combined_results.rename(columns={
        'Combined Total Value': 'Combined Total Value (£)'
    })
    
    # Format for display
    display_combined_df = filtered_combined_results.copy()
    
    # Format indices as strings ('2025', '2026', etc.)
    display_combined_df.index = display_combined_df.index.map(lambda x: f'{x}')
    
    # Format combined value with NO decimal places, only thousands separator
    display_combined_df['Combined Total Value (£)'] = display_combined_df['Combined Total Value (£)'].apply(lambda x: f"£{int(x):,}")
    
    # Display the combined results table
    st.dataframe(display_combined_df, use_container_width=True)
    
    # Download button for detailed results
    csv = results.to_csv(index=True)
    st.download_button(
        label="Download detailed results as CSV",
        data=csv,
        file_name="equity_redemption_results.csv",
        mime="text/csv",
    )
    
    # Visualizations section - reorganized and without 2035 values
    st.header("Grant Value Visualizations")
    
    # CHART 1: Common Share Value at Various Redemption Rates (first)
    st.write("### Common Share Grant Value at Various Redemption Rates")
    
    # Calculate data for different common share redemption rates
    chart_common_data = pd.DataFrame(index=range(2025, 2035))  # Exclude 2035
    
    # Add lines for different common redemption rates
    common_redemption_rates = [0.0, 0.05, 0.10]
    for rate in common_redemption_rates:
        results_for_rate = calculate_values(
            redemption_percentage, 
            pbt_growth_rate, 
            vested_shares_input,
            rate,
            total_common_shares,
            common_purchase_price
        )
        chart_common_data[f"{int(rate*100)}% Common Redemption"] = results_for_rate.loc[2025:2034, 'Total Common Share Value']  # Exclude 2035
    
    # Convert index to strings for better display
    chart_common_data.index = chart_common_data.index.map(str)
    
    # Display the chart
    st.line_chart(chart_common_data)
    
    # CHART 2: A-Share/Options Value at Various Redemption Rates (second)
    st.write("### A-Share/Options Grant Value at Various Redemption Rates")
    
    # Calculate data for different redemption rates using the user's vesting schedule
    chart_option_data = pd.DataFrame(index=range(2025, 2035))  # Exclude 2035
    
    # Add lines for different redemption rates
    option_redemption_rates = [0.0, 0.05, 0.10]
    for rate in option_redemption_rates:
        results_for_rate = calculate_values(
            rate, 
            pbt_growth_rate, 
            vested_shares_input,
            common_redemption_percentage,
            total_common_shares,
            common_purchase_price
        )
        chart_option_data[f"{int(rate*100)}% Option Redemption"] = results_for_rate.loc[2025:2034, 'Total Grant Value']  # Exclude 2035
    
    # Convert index to strings for better display
    chart_option_data.index = chart_option_data.index.map(str)
    
    # Display the chart
    st.line_chart(chart_option_data)
    
    # CHART 3: Combined Value with different growth rates (assuming no redemption)
    st.write("### Combined Total Value at Different PBT Growth Rates")
    st.write("*Assuming no share redemption*")
    
    # Calculate data for different growth rates
    chart_combined_data = pd.DataFrame(index=range(2025, 2035))  # Exclude 2035
    
    # Add lines for different growth rates with NO REDEMPTION
    growth_rates = [0.15, 0.20]
    for rate in growth_rates:
        results_for_growth = calculate_values(
            0.0,  # No redemption for A-Shares/Options
            rate, 
            vested_shares_input,
            0.0,  # No redemption for Common Shares
            total_common_shares,
            common_purchase_price
        )
        chart_combined_data[f"{int(rate*100)}% Growth"] = results_for_growth.loc[2025:2034, 'Combined Total Value']  # Exclude 2035
    
    # Convert index to strings for better display
    chart_combined_data.index = chart_combined_data.index.map(str)
    
    # Display the chart
    st.line_chart(chart_combined_data)

except Exception as e:
    st.error(f"An error occurred in the calculation: {str(e)}")
    st.write("Please check your inputs and try again.")

# Add a footer
st.markdown("---")
st.caption("OakNorth Grants Working Sheet © 2025")
