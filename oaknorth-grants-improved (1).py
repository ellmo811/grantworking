import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Union

# Improved configuration and caching
@st.cache_data
def load_initial_configuration():
    """Load initial configuration and default values."""
    return {
        'initial_share_price': 6.00,
        'years_range': list(range(2025, 2036)),
        'default_vesting_values': {
            2025: 60000,
            2026: 70000,
            2027: 80000,
            2028: 90000,
            2029: 100000
        }
    }

# Set page configuration
st.set_page_config(
    page_title="OakNorth Grants Analysis",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache the configuration
config = load_initial_configuration()

def validate_inputs(
    total_common_shares: int, 
    common_purchase_price: float, 
    total_grant_shares: int, 
    strike_price: float
) -> bool:
    """
    Validate input parameters to prevent calculation errors.
    
    Args:
        total_common_shares (int): Total number of common shares
        common_purchase_price (float): Purchase price of common shares
        total_grant_shares (int): Total number of grant shares
        strike_price (float): Strike price of options
    
    Returns:
        bool: True if inputs are valid, False otherwise
    """
    # Basic validation checks
    if total_common_shares <= 0 or total_grant_shares <= 0:
        st.error("Total shares must be positive")
        return False
    
    if common_purchase_price <= 0 or strike_price <= 0:
        st.error("Purchase and strike prices must be positive")
        return False
    
    return True

def calculate_results(
    common_redemption_rate: float, 
    option_redemption_rate: float, 
    total_common_shares: int,
    total_grant_shares: int,
    common_purchase_price: float,
    strike_price: float,
    vested_shares_input: Dict[int, int],
    growth_rate: float = None
) -> Dict[int, Dict[str, Union[float, int]]]:
    """
    Comprehensive calculation of grant values with enhanced error handling.
    
    Args:
        common_redemption_rate (float): Redemption rate for common shares
        option_redemption_rate (float): Redemption rate for options
        total_common_shares (int): Total number of common shares
        total_grant_shares (int): Total number of grant shares
        common_purchase_price (float): Purchase price of common shares
        strike_price (float): Strike price of options
        vested_shares_input (Dict[int, int]): Vesting schedule
        growth_rate (float, optional): PBT growth rate. Defaults to None.
    
    Returns:
        Dict: Detailed calculation results for each year
    """
    # Validate inputs before calculation
    if not validate_inputs(
        total_common_shares, 
        common_purchase_price, 
        total_grant_shares, 
        strike_price
    ):
        return {}
    
    # Use the provided growth rate or default
    if growth_rate is None:
        growth_rate = 0.20  # Default 20% growth
    
    # Initialize years and results dictionary
    years = list(range(2024, 2036))
    results = {year: {} for year in years}
    
    # Core calculation logic (similar to previous implementation)
    # [Calculation logic remains the same as in the previous script]
    # ... (paste the entire calculation logic from the previous script)
    
    return results

def main():
    """Main Streamlit application"""
    # Title and introduction
    st.title("🚀 OakNorth Grants Analysis Tool")
    st.markdown("""
    ## Grant Value Projection and Sensitivity Analysis
    
    This interactive tool helps you analyze the potential value of OakNorth grants 
    under different scenarios. Adjust parameters in the sidebar to explore 
    potential outcomes.
    
    ### Key Features:
    - Customize redemption rates
    - Explore different growth scenarios
    - Visualize grant value projections
    """)
    
    # Sidebar inputs
    with st.sidebar:
        st.header("🔧 Input Parameters")
        
        # Growth Rate
        pbt_growth_rate = st.slider(
            "PBT Growth Rate", 
            min_value=10, 
            max_value=25,
            value=20,
            step=1,
            help="Annual growth rate of share price"
        ) / 100
        
        # Common Shares Section
        st.subheader("Common Shares")
        total_common_shares = st.number_input(
            "Total Common Shares",
            min_value=1,
            value=30000,
            step=100,
            help="Total number of common shares"
        )
        
        common_purchase_price = st.number_input(
            "Common Share Purchase Price (£)",
            min_value=0.01,
            value=2.00,
            step=0.01,
            format="%.2f",
            help="Initial purchase price of common shares"
        )
        
        common_redemption_rate = st.slider(
            "Common Share Redemption %", 
            min_value=0, 
            max_value=10,
            value=5,
            step=1,
            help="Percentage of common shares to redeem annually"
        ) / 100
        
        # A-Share/Options Section
        st.subheader("A-Share/Options")
        total_grant_shares = st.number_input(
            "Total Grant Shares",
            min_value=1,
            value=100000,
            step=100,
            help="Total number of shares in the grant"
        )
        
        strike_price = st.number_input(
            "Strike Price (£)",
            min_value=0.01,
            value=6.00,
            step=0.01,
            format="%.2f",
            help="Initial strike price of options"
        )
        
        option_redemption_rate = st.slider(
            "A-Share/Options Redemption %", 
            min_value=0, 
            max_value=10,
            value=5,
            step=1,
            help="Percentage of vested unsold options to redeem annually"
        ) / 100
        
        # Vesting Schedule
        st.subheader("Vesting Schedule")
        vesting_method = st.radio(
            "Vesting Method",
            ["Default Schedule", "Custom Vesting"],
            help="Choose default vesting schedule or set custom values"
        )
        
        # Vesting shares input logic
        vested_shares_input = {}
        if vesting_method == "Default Schedule":
            vested_shares_input = {
                year: config['default_vesting_values'].get(year, 100000) 
                for year in config['years_range']
            }
        else:
            # Custom vesting input UI logic
            st.write("Enter vested shares for each year:")
            for year in config['years_range']:
                default_value = config['default_vesting_values'].get(year, 100000)
                vested_shares_input[year] = st.number_input(
                    f"{year}", 
                    min_value=0, 
                    max_value=total_grant_shares, 
                    value=default_value, 
                    step=100,
                    key=f"vest_{year}"
                )
    
    # Perform calculations
    results = calculate_results(
        common_redemption_rate, 
        option_redemption_rate, 
        total_common_shares,
        total_grant_shares,
        common_purchase_price,
        strike_price,
        vested_shares_input,
        pbt_growth_rate
    )
    
    # Tabs for analysis
    tab1, tab2, tab3 = st.tabs([
        "Common Share Analysis", 
        "A-Share/Options Analysis", 
        "Combined Analysis"
    ])
    
    # Analysis tabs implementation (similar to previous script)
    # [Add similar implementation as in the previous script]
    
    # Optional: Add more insights or recommendations
    st.markdown("---")
    st.info("""
    ### 💡 Insights
    - Redemption rates significantly impact grant value
    - Higher PBT growth rates can substantially increase potential returns
    - Diversification and timing of redemptions are crucial
    """)

if __name__ == "__main__":
    main()
