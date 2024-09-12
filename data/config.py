from bs4 import BeautifulSoup as bts
import requests
import time, os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import warnings
warnings.filterwarnings(action='ignore')
query="https://www.meteociel.fr/temps-reel/obs_villes.php?"
driver = webdriver.Chrome()
driver.get(query)

# Locate the elements
hours_time_elements = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '/html/body/table[1]/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td/center[4]/table[2]/tbody/tr/td[1]'))
)
wind_speed_elements = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '/html/body/table[1]/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td/center[4]/table[2]/tbody/tr/td[9]'))
)

# Ensure both lists have the same length
length = min(len(hours_time_elements), len(wind_speed_elements))

# Create the archive list
archive_list = []
for i in range(length):
    temprory_data = {
        'hours_time': hours_time_elements[i].text,
        'wind_speed': wind_speed_elements[i].text
    }
    archive_list.append(temprory_data)

# Convert to DataFrame
df_archive_list = pd.DataFrame(archive_list)
df_archive_list
#save the data
df_archive_list.to_csv('archive_list.csv', index=False)