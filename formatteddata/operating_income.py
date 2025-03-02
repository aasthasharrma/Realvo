import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.macrotrends.net/stocks/charts/SPG/simon-property/operating-income"

#Send a get request to fetch webpage information

headers = {"User-agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)

#check whether request succeeded
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    #Find all tables on the page
    tables = soup.find_all("table")

    #Extract only important data
    data_quarterly = []

    for table in tables:
        if "Quarterly Operating Income" in table.text:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                cols = [col.text.strip() for col in cols]
                if len(cols) == 2:
                    data_quarterly.append(cols)
    
    df_quarterly = pd.DataFrame(data_quarterly, columns=["Date", "Quarterly Operating Income"])

    df_quarterly.to_csv("SPG_Quarterly_Operating_Income.csv", index=False)

    print("Quarterly operating income data has been scraped and saved successfuly")
else:
    print("Failed to retrieve data")