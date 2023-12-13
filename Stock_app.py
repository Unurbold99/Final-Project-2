import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to scrape data for a specific company and return the DataFrame
@st.cache
def scrape_company_data(url):
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
                        data.append({'Highest Price': second_column, 'Volume': sixth_column, 'Date': eighth_column})

                df = pd.DataFrame(data)
                return df
            else:
                st.warning("No tbody found in the table.")
        else:
            st.warning("No table with the specified class found.")
    else:
        st.warning(f"Failed to retrieve the webpage. Status Code: {response.status_code}")

# Streamlit App
st.title("Stock Price Data App")

# Button to trigger scraping for all companies
if st.button("Scrape Top 20 data"):
    starting_url = 'https://www.mse.mn/en/mse_top_20/266'
    response = requests.get(starting_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='table dividend trade_table table-bordered table-striped table-hover table-condensed')

        if table:
            tbody = table.find('tbody')

            if tbody:
                company_data = {}
                for row in tbody.find_all('tr'):
                    link = row.find('a')
                    if link:
                        href = link.get('href')
                        full_url = f"https://www.mse.mn{href}"
                        company_name = link.get_text(strip=True)

                        # Scrape data for the current company
                        df = scrape_company_data(full_url)

                        # Store the DataFrame for the current company
                        company_data[company_name] = df

    st.success("Data successfully scraped!")

# Check if company_data is defined (i.e., if the button has been pressed)
if 'company_data' in locals():
    # Select box for company names
    selected_company = st.selectbox("Select a Company", list(company_data.keys()), key="company_select")

    # Display the selected company's data
    st.write(f"Data for {selected_company}:\n{company_data[selected_company]}")
