import re
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def fetch_monthly_weather_data(station_code: str, start_date: str, end_date: str, driver_path: str) -> pd.DataFrame:
    """
    Scrapes wind speed and gust data for each hour from the Meteociel website and converts it to a DataFrame.
    
    Parameters:
    - station_code: str, the code of the weather station.
    - start_date: str, the start date in 'YYYY-MM-DD' format.
    - end_date: str, the end date in 'YYYY-MM-DD' format.
    - driver_path: str, the path to the ChromeDriver executable.
    
    Returns:
    - pd.DataFrame: DataFrame containing the scraped data.
    """
    data = []
    
    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Set up the Selenium WebDriver
    options = Options()
    options.headless = False  # Set to True if you don't want to see the browser window
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    current_date = start_date
    while current_date <= end_date:
        day = current_date.day
        month = current_date.month - 1  # Adjust for mois2 being 0-based
        year = current_date.year
        
        url = f"https://www.meteociel.fr/temps-reel/obs_villes.php?code2={station_code}&jour2={day}&mois2={month}&annee2={year}"
        print(f"Fetching data for {current_date.strftime('%Y-%m-%d')}: {url}")
        driver.get(url)
        
        time.sleep(5)  # Wait for the page to load completely
        
        try:
            table_xpath = "/html/body/table[1]/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td/center[4]/table[2]"
            table = driver.find_element(By.XPATH, table_xpath)
            rows = table.find_elements(By.XPATH, "./tbody/tr")
            
            if not rows:
                print(f"No data found for {current_date.strftime('%Y-%m-%d')}")
                continue
            
            for row in rows:
                try:
                    time_str = row.find_element(By.XPATH, "./td[1]").text.strip()
                    wind_speed_str = row.find_element(By.XPATH, "./td[11]/div").text.strip()
                    
                    print(f"Raw time data: {time_str}, Raw wind data: {wind_speed_str}")
                    
                    # Adjust the regular expression to handle both formats
                    time_match = re.search(r'(\d{1,2})\s?h(\d{2})?', time_str)
                    if not time_match:
                        continue
                    
                    hour = time_match.group(1)
                    minute = time_match.group(2) if time_match.group(2) else "00"
                    time_str = f"{hour}:{minute}"
                    
                    wind_speed, wind_gust = parse_wind_data(wind_speed_str)
                    
                    time_value = datetime.strptime(f"{year}-{current_date.month:02d}-{day:02d} {time_str}", '%Y-%m-%d %H:%M')
                    
                    data.append({
                        'DateTime': time_value,
                        'WindSpeed (km/h)': wind_speed,
                        'WindGust (km/h)': wind_gust
                    })
                
                except Exception as e:
                    print(f"Error processing row: {e}")
        
        except Exception as e:
            print(f"Error accessing data for {current_date.strftime('%Y-%m-%d')}: {e}")
        
        current_date += timedelta(days=1)
    
    driver.quit()
    return pd.DataFrame(data)

def parse_wind_data(wind_speed_str: str):
    """
    Parses the wind speed and gust data from a string.
    
    Parameters:
    - wind_speed_str: str, the raw wind speed string.
    
    Returns:
    - tuple: (wind_speed, wind_gust) as floats or None if not available.
    """
    wind_data_match = re.match(r'(\d+)\s*km/h(?:\s*\((\d+)\s*km/h\))?', wind_speed_str)
    if wind_data_match:
        wind_speed = float(wind_data_match.group(1))
        wind_gust = float(wind_data_match.group(2)) if wind_data_match.group(2) else None
        return wind_speed, wind_gust
    else:
        print(f"Wind data did not match expected format: {wind_speed_str}")
        return None, None

# Example usage for August 2024
if __name__ == "__main__":
    station_code = "17109"
    start_date = "2024-08-30"
    end_date = "2024-08-31"
    driver_path = "/Users/fatihbayram/Documents/GitHub/wind_forecast/chromedriver"  # Update this path to your ChromeDriver executable

    df = fetch_monthly_weather_data(station_code=station_code, start_date=start_date, end_date=end_date, driver_path=driver_path)
    print(df)
    df.to_csv(f'weather_data_{station_code}_{start_date}_{end_date}.csv', index=False)