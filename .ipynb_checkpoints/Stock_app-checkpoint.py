import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Function to fit a parabola
def parabola(x, a, b, c):
    return a * x**2 + b * x + c

# Starting URL to scrape the 20 URLs
starting_url = 'https://www.mse.mn/en/mse_top_20/266'

# Function to scrape data
def scrape_data():
    # Fetch the HTML content of the webpage
    response = requests.get(starting_url)
    html_content = response.content

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', class_='table dividend trade_table table-bordered table-striped table-hover table-condensed')

        # Check if the table is found
        if table:
            tbody = table.find('tbody')

            # Check if tbody is found
            if tbody:
                urls = []
                names = []  # New list to store the text from <a> tags
                for row in tbody.find_all('tr'):
                    link = row.find('a')
                    if link:
                        href = link.get('href')
                        full_url = f"https://www.mse.mn{href}"
                        urls.append(full_url)

                        # Extract text from <a> tag and append to names list
                        name_text = link.get_text(strip=True)
                        names.append(name_text)

                # Create DataFrame with URLs and Names columns
                url_df = pd.DataFrame({'URLs': urls, 'Names': names})
                return url_df
            else:
                st.warning("No tbody found in the table.")
        else:
            st.warning("No table with the specified class found.")
    else:
        st.error(f"Failed to retrieve the webpage. Status Code: {response.status_code}")

# Function to plot historical stock prices
def plot_stock_prices(df):
    st.subheader("Historical Stock Prices")
    
    # Selectbox for choosing a company
    selected_company = st.selectbox("Select a Company", df['Company'].unique())

    # Filter DataFrame based on selected company
    selected_df = df[df['Company'] == selected_company]

    # Date range selection
    start_date = st.date_input("Start Date", min(selected_df['Date']), max(selected_df['Date']))
    end_date = st.date_input("End Date", min(selected_df['Date']), max(selected_df['Date']))

    # Filter DataFrame based on date range
    selected_df = selected_df[(selected_df['Date'] >= start_date) & (selected_df['Date'] <= end_date)]

    # Plot historical stock prices
    plt.figure(figsize=(10, 6))
    plt.plot(selected_df['Date'], selected_df['Highest Price'], label='Highest Price', marker='o')
    
    # Fit a linear trend
    linear_params = np.polyfit(np.arange(len(selected_df)), selected_df['Highest Price'], 1)
    linear_trend = np.polyval(linear_params, np.arange(len(selected_df)))
    plt.plot(selected_df['Date'], linear_trend, label='Linear Trend', linestyle='--')

    # Fit a parabola (quadratic trend)
    params, _ = curve_fit(parabola, np.arange(len(selected_df)), selected_df['Highest Price'])
    parabolic_trend = parabola(np.arange(len(selected_df)), *params)
    plt.plot(selected_df['Date'], parabolic_trend, label='Parabolic Trend', linestyle='--')

    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title(f'{selected_company} Stock Prices')
    plt.legend()
    st.pyplot()

# Streamlit app
def main():
    st.title("Stock Price Analysis App")

    # Button to trigger data scraping
    if st.button("Scrape Data"):
        url_df = scrape_data()
        if url_df is not None:
            st.success("Data Scraped Successfully!")
        else:
            st.error("Failed to Scrape Data.")

    # Check if DataFrame is available
    if 'url_df' in locals() or 'url_df' in globals():
        # List to store DataFrames for each URL
        dfs = []

        # Loop over each row in the DataFrame and scrape data
        for i, row in url_df.iterrows():
            # Extract the URL and name from the row
            url = row['URLs']
            company_name = row['Names']

            # Fetch the HTML content of the webpage
            response = requests.get(url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                html = response.text

                # Parse the HTML using BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')

                # Find the table with the specified class
                table = soup.find('table', class_='table table-bordered trade_history_result table-striped table-hover table-condensed')

                # Check if the table is found
                if table:
                    # Find the table body
                    tbody = table.find('tbody')

                    # Check if tbody is found
                    if tbody:
                        # List to store data for each row
                        data = []

                        # Iterate over each row in the table body and extract the desired data
                        for row in tbody.find_all('tr'):
                            # Find all 'td' elements in the current row
                            columns = row.find_all('td')

                            # Extract the 2nd, 6th, and 8th 'td' elements
                            if len(columns) >= 8:
                                second_column = columns[1].text.strip()
                                sixth_column = columns[5].text.strip()
                                eighth_column = columns[7].text.strip()

                                # Append the data as a dictionary to the list
                                data.append({'Highest Price': second_column, 'Volume': sixth_column, 'Date': eighth_column, 'Company': company_name})

                        # Convert the list of dictionaries to a DataFrame
                        df = pd.DataFrame(data)

                        # Append the DataFrame to the list
                        dfs.append(df)

                        # Optionally, you can display the DataFrame
                        st.write(f"Data for {company_name}:\n{df}\n" + "="*40 + "\n")
                    else:
                        st.warning(f"No tbody found in the table for {company_name}")
                else:
                    st.warning(f"No table with the specified class found for {company_name}")
            else:
                st.error(f"Failed to retrieve the webpage. Status Code: {response.status_code}")

        # Combine all DataFrames into a single DataFrame if needed
        combined_df = pd.concat(dfs, ignore_index=True)

        # Plot historical stock prices
        plot_stock_prices(combined_df)

if __name__ == "__main__":
    main()
