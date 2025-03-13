from uuid import uuid4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

from models.models import Outlet

url = "https://subway.com.my/find-a-subway"
input_id = "fp_searchAddress"
button_id = "fp_searchAddressBtn"
data_class_name = "fp_listitem"
search_string = "kuala lumpur"
location_list_id = "fp_locationlist"

 # Define weekdays to filter operating hours
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def scrape_data(headless=True):
    # Set up Chrome Web Driver options
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--log-level=1")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Open the website
        driver.get(url)

        # Wait for the input field and enter search text
        wait = WebDriverWait(driver, 10)
        input_field = wait.until(EC.presence_of_element_located((By.ID, input_id)))
        input_field.clear()  # Clear any existing text
        input_field.send_keys(search_string)  # Enter the search query

        # Wait for the search button and click it
        search_button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
        search_button.click()

        # Handle any alerts
        handle_alert(driver)

        # Wait for the results to appear
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, data_class_name)))

         # Extract data
        elements = [element for element in driver.find_elements(By.XPATH, "//div[@id='{}']//div[contains(@class, '{}')]".format(location_list_id, data_class_name)) if "display: none" not in element.get_attribute("style")]
        results = []

        for i, element in enumerate(elements):
            try:
                # Extracting details
                name = element.find_element(By.TAG_NAME, "h4").text
                address = element.find_element(By.CLASS_NAME, "infoboxcontent").find_element(By.TAG_NAME, "p").text
                
                # handle empty address
                if not address:
                    address = None

                # Extract latitude and longitude
                latitude = element.get_attribute("data-latitude")
                longitude = element.get_attribute("data-longitude")
                
                # Extract operating hours by checking for weekday names
                all_paragraphs = element.find_element(By.CLASS_NAME, "infoboxcontent").find_elements(By.TAG_NAME, "p")
                operating_hours = [p.text for p in all_paragraphs if any(day in p.text for day in weekdays)]

                # Allow empty operating hours if none are found
                if not operating_hours:
                    operating_hours = None
                else:
                    # Join the operating hours into a single string with newlines
                    operating_hours = "\n".join(operating_hours)

                # Extract Waze link
                waze_link = element.find_element(By.CLASS_NAME, "directionButton").find_elements(By.TAG_NAME, "a")[1].get_attribute("href")
                waze_link = fix_duplicated_link(waze_link)

                result  = Outlet(
                    id = uuid4(),
                    name=name,
                    address=address,
                    operating_hours=operating_hours,
                    waze_link=waze_link,
                    latitude=latitude,
                    longitude=longitude
                )

                results.append(result)

                # print progress
                print(f"Progress: {i+1}/{len(elements)}")

            except UnexpectedAlertPresentException:
                handle_alert(driver)

            except Exception as e:
                print(f"Skipping element: {e}")

        return results

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        driver.quit()  # Close the browser


def handle_alert(driver):
    """Handles unexpected alerts by dismissing them."""
    try:
        alert = driver.switch_to.alert
        print(f"Alert detected: {alert.text}")
        alert.dismiss()  # Close the alert
    except NoAlertPresentException:
        pass  # No alert found

def fix_duplicated_link(url):
    """
    Handles duplicated links by extracting only the first occurrence.
    
    Args:
        url (str): The potentially duplicated URL string
        
    Returns:
        str: The fixed URL with only the first occurrence
    """
    # Check for common URL prefixes to identify where links might be duplicated
    common_prefixes = ["http://", "https://", "www."]
    
    for prefix in common_prefixes:
        # Find the second occurrence of the prefix if it exists
        first_occurrence = url.find(prefix)
        if first_occurrence >= 0:
            second_occurrence = url.find(prefix, first_occurrence + 1)
            if second_occurrence >= 0:
                # Return only the portion up to the second occurrence
                return url[:second_occurrence]
    
    # If no duplication found, return the original URL
    return url



