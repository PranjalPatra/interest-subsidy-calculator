import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# Updated data for interest rate changes
interest_rate_changes = [
    ("2024-06-06", 6.950),
    ("2023-07-13", 7.200),
    ("2023-06-08", 6.950),
    ("2023-01-26", 6.700),
    ("2022-12-08", 6.450),
    ("2022-10-27", 5.950),
    ("2022-09-08", 5.450),
    ("2022-07-14", 4.700),
    ("2022-06-02", 3.700),
    ("2022-04-14", 3.200),
    ("2022-03-03", 2.700),
    ("2020-03-30", 2.450),
    ("2020-03-17", 2.950),
    ("2020-03-05", 3.450),
    ("2018-10-25", 3.950),
    ("2018-07-12", 3.700),
    ("2018-01-18", 3.450),
    ("2017-09-07", 3.200),
    ("2017-07-13", 2.950),
    ("2015-07-17", 2.700),
    ("2015-07-16", 2.750),
    ("2015-01-28", 2.850),
]

# Convert to DataFrame for easier manipulation
rate_df = pd.DataFrame(interest_rate_changes, columns=["Date", "PrimeRate"])
rate_df["Date"] = pd.to_datetime(rate_df["Date"])

def calculate_subsidy_cost(loan_amount, subsidy_rate, rate_df, start_date, end_date):
    rate_df = rate_df.sort_values("Date")
    rate_df = rate_df[(rate_df["Date"] >= start_date) & (rate_df["Date"] <= end_date)]
    rate_df = rate_df.reset_index(drop=True)

    detailed_calculations = []
    total_interest_no_subsidy = 0
    total_subsidy_cost = 0
    cumulative_subsidy = 0
    current_date = start_date
    previous_rate = rate_df.iloc[0]["PrimeRate"]
    
    for index, row in rate_df.iterrows():
        rate_date = row["Date"]
        prime_rate = row["PrimeRate"]
        
        if rate_date > end_date:
            rate_date = end_date

        days = (rate_date - current_date).days
        interest_no_subsidy = loan_amount * (previous_rate / 100) * (days / 365)
        discounted_rate = previous_rate - (subsidy_rate * 100)
        if discounted_rate < 0:
            discounted_rate = 0
        interest_with_subsidy = loan_amount * (discounted_rate / 100) * (days / 365)
        subsidy = interest_no_subsidy - interest_with_subsidy
        cumulative_subsidy += subsidy
        
        detailed_calculations.append({
            "From": current_date.strftime('%Y-%b-%d').upper(),
            "To": rate_date.strftime('%Y-%b-%d').upper(),
            "Days": days,
            "Prime rate": previous_rate,
            "Discounted rate": discounted_rate,
            "Interest without Subsidy": f"${interest_no_subsidy:,.2f}",
            "Subsidy": f"${subsidy:,.2f}",
            "Cumulative Subsidy": f"${cumulative_subsidy:,.2f}",
            "Interest with Subsidy": f"${interest_with_subsidy:,.2f}"
        })
        
        total_interest_no_subsidy += interest_no_subsidy
        total_subsidy_cost += subsidy
        
        current_date = rate_date
        previous_rate = prime_rate
        
        if current_date >= end_date:
            break

    return total_subsidy_cost, total_interest_no_subsidy, detailed_calculations

# Streamlit app
st.title('Interest Subsidy Calculator')

# User inputs
loan_amount = st.number_input('Loan Amount', value=100)
subsidy_rate = float(st.number_input('Subsidy Rate', value=2.5)/100) #2.5 / 100  # Fixed subsidy rate of 2.5%
start_date = st.date_input('Start Date', value=datetime(2019, 6, 1))
end_date = st.date_input('End Date', value=datetime(2024, 5, 31))

# Convert dates to datetime
start_date = datetime.combine(start_date, datetime.min.time())
end_date = datetime.combine(end_date, datetime.min.time())

# Calculate the total subsidy cost and detailed breakdown
if st.button('Calculate'):
    total_cost, total_interest, details = calculate_subsidy_cost(loan_amount, subsidy_rate, rate_df, start_date, end_date)

    # Display results
    st.write(f"The total subsidy cost over the period is: ${total_cost:,.2f}")
    st.write(f"The total interest without subsidy over the period is: ${total_interest:,.2f}\n")
    
    # Display detailed calculations in a table format
    st.subheader('Detailed Calculations')
    detailed_df = pd.DataFrame(details)
    st.dataframe(detailed_df.style.set_properties(**{'width': '250px'}))

    st.write('Note: Discounted Rate will not go below 0%.')

