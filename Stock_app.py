import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

# Function to scrape data for a specific company
def scrape_data(url, company_name):
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find('table', class_='table table-bordered trade_history_result table-striped table-hover table-condensed')

        if table:
            tbody = table.find('tbody')

            if tbody:
                data = []

                for row in tbody.find_all('tr'):
                    columns = row.find_all('td')

                    if len(columns) >= 8:
                        second_column = columns[1].text.strip()
                        sixth_column = columns[5].text.strip()
                        eighth_column = columns[7].text.strip()

                        data.append({'Highest Price': second_column, 'Volume': sixth_column, 'Date': eighth_column, 'Company': company_name})

                df = pd.DataFrame(data)
                return df
            else:
                st.warning(f"No tbody found in the table for {company_name}")
        else:
            st.warning(f"No table with the specified class found for {company_name}")
    else:
        st.error(f"Failed to retrieve the webpage for {company_name}. Status Code: {response.status_code}")
        return None

# Load the data initially
starting_url = 'https://www.mse.mn/en/mse_top_20/266'
response = requests.get(starting_url)
html_content = response.content

if response.status_code == 200:
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='table dividend trade_table table-bordered table-striped table-hover table-condensed')

    if table:
        tbody = table.find('tbody')

        if tbody:
            urls = []
            names = []
            for row in tbody.find_all('tr'):
                link = row.find('a')
                if link:
                    href = link.get('href')
                    full_url = f"https://www.mse.mn{href}"
                    urls.append(full_url)

                    name_text = link.get_text(strip=True)
                    names.append(name_text)

            url_df = pd.DataFrame({'URLs': urls, 'Names': names})
        else:
            st.warning("No tbody found in the table.")
    else:
        st.warning("No table with the specified class found.")
else:
    st.error(f"Failed to retrieve the webpage. Status Code: {response.status_code}")

# Streamlit app
st.title("Stock Price Analysis")

# Selectbox to choose a company
selected_company = st.selectbox("Select a company:", url_df['Names'])

# Input box for the period (in months)
period_months = st.number_input("Enter the period (in months):", min_value=1, value=6)

# Button to trigger data scraping and graph display
if st.button("Show Graph"):
    st.subheader(f"Stock Price Analysis for {selected_company}")
    
    # Get the selected company's URL
    selected_url = url_df.loc[url_df['Names'] == selected_company, 'URLs'].iloc[0]

    # Scrape data for the selected company
    selected_data = scrape_data(selected_url, selected_company)

    if selected_data is not None:
        # Filter data for the specified period
        today = pd.to_datetime(datetime.date.today())
        start_date = today - pd.DateOffset(months=period_months)
        selected_data['Date'] = pd.to_datetime(selected_data['Date'])
        selected_data = selected_data[(selected_data['Date'] >= start_date) & (selected_data['Date'] <= today)]

        # Plot the data using Streamlit line_chart
        st.line_chart(selected_data.set_index('Date')['Highest Price'], use_container_width=True)
