import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import time
import os
import re
import json

from extract_timetable import extract_timetable
from extract_attendance import extract_attendance
from extract_unified_timetable import extract_unified_timetable



def extract_html_content(driver, page_name):
    """Extract raw HTML content from the current page"""
    try:
        # Wait for content to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "zc-component"))
        )
        
        # Get page source
        page_source = driver.page_source
        
        return page_source
        
    except Exception as e:
        print(f"❌ Error extracting HTML from {page_name}: {e}")
        return f"Error: Could not extract HTML - {e}"





def scrape_academia_html_data(email, password, headless=False):
    """
    Scrapes text data from the SRM Academia portal.
    
    Args:
        email (str): User's email/login ID
        password (str): User's password
        headless (bool): Whether to run browser in headless mode (default: False)
    
    Returns:
        dict: Dictionary containing collected text data from all pages
    """
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    if headless:
        # Run Chrome in headless mode (no GUI window)
        chrome_options.add_argument("--headless")
        # Additional options to run in background without interruption
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # Suppress logging output
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://academia.srmist.edu.in/")

        # Wait for the page to load
        time.sleep(3)

        # Switch to the iframe that contains the login form
        iframe = driver.find_element(By.ID, "signinFrame")
        driver.switch_to.frame(iframe)

        # Wait for the email input field to be present and enter the email
        try:
            # Wait for the email input field to be clickable
            email_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "LOGIN_ID"))
            )
            
            # Clear any existing text and enter the email
            email_input.clear()
            email_input.send_keys(email) 
            
            print(f"Successfully entered email: {email}")
            
            # Find and click the login/next button
            # Look for common login button identifiers
            login_button = None
            
            # Try different selectors for the login button
            button_selectors = [
                (By.ID, "nextbtn"),
                (By.NAME, "Submit"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Next')]"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.CLASS_NAME, "signin-btn"),
                (By.XPATH, "//input[@value='Next']")
            ]
            
            for selector_type, selector_value in button_selectors:
                try:
                    login_button = driver.find_element(selector_type, selector_value)
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
                print("Successfully clicked the login button")
                
                # Wait for the password field to appear
                time.sleep(2)
                
                # Try to find the password field
                try:
                    password_input = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, "PASSWORD"))
                    )
                    
                    # Clear any existing text and enter the password
                    password_input.clear()
                    password_input.send_keys(password)
                    
                    print("Successfully entered password")
                    
                    # Look for the final login/submit button after password
                    final_login_button = None
                    
                    # Try different selectors for the final login button
                    final_button_selectors = [
                        (By.ID, "nextbtn"),
                        (By.NAME, "Submit"),
                        (By.XPATH, "//input[@type='submit']"),
                        (By.XPATH, "//button[contains(text(), 'Sign In')]"),
                        (By.XPATH, "//button[contains(text(), 'Login')]"),
                        (By.CLASS_NAME, "signin-btn"),
                        (By.XPATH, "//input[@value='Sign In']"),
                        (By.XPATH, "//input[@value='Login']")
                    ]
                    
                    for selector_type, selector_value in final_button_selectors:
                        try:
                            final_login_button = driver.find_element(selector_type, selector_value)
                            break
                        except:
                            continue
                    
                    if final_login_button:
                        final_login_button.click()
                        print("Successfully clicked the final login button")
                    else:
                        print("Could not find the final login button")
                        
                except Exception as password_error:
                    print(f"Password field error: {password_error}")
                    print("Current page source after email submission:")
                    print(driver.page_source[:1500])  # Print more characters to see password field
                    
            else:
                print("Could not find the login button")
                
        except Exception as e:
            print(f"Error: {e}")
            # Print the page source of the iframe to help debug
            print("Current page source:")
            print(driver.page_source[:1000])  # Print first 1000 characters

        # Switch back to the main content
        driver.switch_to.default_content()

        print("Login process completed.")

        # Wait a moment for the page to fully load after login
        time.sleep(5)

        # Navigate to specific pages and collect data
        print("\n" + "="*50)
        print("STARTING HTML DATA COLLECTION FROM PORTAL PAGES")
        print("="*50)

        # Dictionary to store collected data
        collected_data = {}

        # Define pages to scrape
        pages = [
            ("My_Time_Table_2023_24", "https://academia.srmist.edu.in/#Page:My_Time_Table_2023_24"),
            ("Unified_Time_Table_2025_batch_2", "https://academia.srmist.edu.in/#Page:Unified_Time_Table_2025_batch_2"),
            ("My_Attendance", "https://academia.srmist.edu.in/#Page:My_Attendance")
        ]
        if "structured_data" not in os.listdir():
            os.mkdir("structured_data")

        for i, (page_name, url) in enumerate(pages, 1):
            print(f"\n{i}. Navigating to {page_name.replace('_', ' ')}...")
            driver.get(url)
            time.sleep(7)  # Wait longer for page to load completely
            
            html_content = extract_html_content(driver, page_name)
            
            
            if page_name == "My_Attendance":
                attendance_data, marks_data = extract_attendance(html_content)
                
                attendance_file = os.path.join("structured_data", "attendance_data.json")
                marks_file = os.path.join("structured_data", "marks_data.json")
                try:
                    with open(attendance_file, "w", encoding="utf-8") as f_att:
                        json.dump(attendance_data, f_att, ensure_ascii=False)
                    with open(marks_file, "w", encoding="utf-8") as f_marks:
                        json.dump(marks_data, f_marks, ensure_ascii=False)
                    print("Attendance and marks data written to structured_data folder")
                except Exception as e:
                    print(f"Error writing structured data: {e}")
            if page_name == "My_Time_Table_2023_24":
                timetable_file = os.path.join("structured_data", "timetable_data.json")
                try:                    
                    timetable_data = extract_timetable(html_content)
                    with open(timetable_file, "w", encoding="utf-8") as f_tt:
                        json.dump(timetable_data, f_tt, ensure_ascii=False)
                    print("Timetable data written to structured_data folder")
                except Exception as e:
                    print(f"Error writing timetable data: {e}")
            if page_name == "Unified_Time_Table_2025_batch_2":
                unified_timetable_file = os.path.join("structured_data", "unified_timetable_data.json")
                try:                    
                    unified_timetable_data = extract_unified_timetable(html_content)
                    with open(unified_timetable_file, "w", encoding="utf-8") as f_utt:
                        json.dump(unified_timetable_data, f_utt, ensure_ascii=False)
                    print("Unified timetable data written to structured_data folder")
                except Exception as e:
                    print(f"Error writing unified timetable data: {e}")
            
            if "Error:" not in html_content:
                collected_data[page_name] = {
                    "html_content": html_content
                }
                print(f"✅ Successfully collected {page_name} HTML data ({len(html_content)} characters)")
            else:
                collected_data[page_name] = {
                    "html_content": html_content
                }
                print(f"❌ {html_content}")

        # Print summary of collected data
        print("\n" + "="*50)
        print("HTML DATA COLLECTION SUMMARY")
        print("="*50)
        for page_name, data in collected_data.items():
            if "Error:" not in data["html_content"]:
                html_length = len(data["html_content"])
                print(f"✅ {page_name}: {html_length:,} characters")
            else:
                print(f"❌ {page_name}: {data['html_content']}")

        # Save the collected data
        print("\n" + "="*50)
        print("SAVING HTML DATA TO FILES:")
        print("="*50)

        # Create sources directory
        if os.path.exists("sources"):
            shutil.rmtree("sources")
        os.mkdir("sources")

        for page_name, data in collected_data.items():
            # Save HTML content
            html_filename = f"sources/{page_name}.html"
            try:
                with open(html_filename, "w", encoding="utf-8") as f:
                    f.write(data["html_content"])
                print(f"📄 HTML data written to {html_filename}")
            except Exception as file_error:
                print(f"Error writing {page_name} HTML data: {file_error}")

        print("\n" + "="*50)
        print("HTML DATA COLLECTION COMPLETED")
        print("="*50)

        # Wait a moment to see the result before closing
        time.sleep(3)

        return collected_data

    finally:
        # Close the browser
        driver.quit()
        print("Browser closed.")

# Example usage - you can call the function with credentials
if __name__ == "__main__":
    # Get credentials from user input
    email = input("Enter mail ID: ")
    password = input("Enter password: ")
    
    # Call the function
    data = scrape_academia_html_data(email, password)
    
    # Print final summary
    print(f"\nFunction completed! Collected data for {len(data)} pages")
    print("HTML files saved in 'sources/' directory")
