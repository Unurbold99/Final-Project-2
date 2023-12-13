import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to scrape data and return the combined DataFrame
@st.cache
def scrape_top_20_data():
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
                dfs = []

                for i, row in url_df.iterrows():
                    url = row['URLs']
                    company_name = row['Names']
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
                                dfs.append(df)
                        else:
                            st.warning(f"No table with the specified class found for {company_name}")
                    else:
                        st.warning(f"Failed to retrieve the webpage. Status Code: {response.status_code}")

                combined_df = pd.concat(dfs, ignore_index=True)
                return combined_df
            else:
                st.warning("No tbody found in the table.")
        else:
            st.warning("No table with the specified class found.")
    else:
        st.warning(f"Failed to retrieve the webpage. Status Code: {response.status_code}")

# Streamlit App
st.title("Stock Price Data App")

# Button to trigger scraping
if st.button("Scrape Top 20 data"):
    scraped_data = scrape_top_20_data()
    st.success("Data successfully scraped!")

# Check if scraped_data is defined (i.e., if the button has been pressed)
if 'scraped_data' in locals():
    # Select box for company names
    selected_company = st.selectbox("Select a Company", scraped_data['Company'].unique(), key="company_select")

    # Filter data based on selected company
    selected_data = scraped_data[scraped_data['Company'] == selected_company]

    # Convert dates to string for slider
    date_range = pd.to_datetime(selected_data['Date'])
    start_date, end_date = st.slider("Select Date Range",
                                     min_value=str(date_range.min().date()),
                                     max_value=str(date_range.max().date()),
                                     value=(str(date_range.min().date()), str(date_range.max().date())))

    # Convert string dates back to Timestamp format
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    # Display wider plot
    st.line_chart(selected_data.set_index('Date')[['Highest Price']], use_container_width=True, width=800)

