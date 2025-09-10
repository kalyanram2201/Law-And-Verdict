import os
import re
import time
import base64
import requests
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_rajasthan_hc(last_n_days=10, reportable="YES", headless=False):
    # Setup Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    wait = WebDriverWait(driver, 30)
    
    # Prepare dates
    to_date = datetime.today()
    from_date = to_date - timedelta(days=last_n_days)
    
    try:
        url = "https://hcraj.nic.in/cishcraj-jdp/JudgementFilters/"
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Fill From Date
        from_inp = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[contains(@id,'from') or contains(@name,'from')]")
            )
        )
        from_inp.clear()
        from_inp.send_keys(from_date.strftime("%d-%m-%Y"))

        # Fill To Date
        to_inp = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[contains(@id,'to') or contains(@name,'to')]")
            )
        )
        to_inp.clear()
        to_inp.send_keys(to_date.strftime("%d-%m-%Y"))

        # Select Reportable = YES
        reportable_dropdown = wait.until(
            EC.presence_of_element_located((By.XPATH, "//select[contains(@id,'reportable')]"))
        )
        for option in reportable_dropdown.find_elements(By.TAG_NAME, "option"):
            if option.text.strip().upper() == reportable.upper():
                option.click()
                break

        # --- CAPTCHA Handling ---
        captcha_img = wait.until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@src,'Captcha')]"))
        )
        captcha_src = captcha_img.get_attribute("src")
        os.makedirs("state", exist_ok=True)
        captcha_path = os.path.join("state", "captcha.png")

        if "base64" in captcha_src:
            with open(captcha_path, "wb") as f:
                f.write(base64.b64decode(captcha_src.split(",")[1]))
        else:
            r = requests.get(captcha_src, stream=True)
            with open(captcha_path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

        print(f"Captcha saved at {captcha_path} – open it and enter the text")
        captcha_text = input("Enter Captcha: ")

        captcha_inp = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'captcha')]"))
        )
        captcha_inp.clear()
        captcha_inp.send_keys(captcha_text)

        # Click Search
        search_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Search')]"))
        )
        search_btn.click()

        # Wait for results table
        wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@class,'table')]")))

        # Scrape rows
        rows = driver.find_elements(By.XPATH, "//table[contains(@class,'table')]//tr")[1:]  # skip header
        data = []
        os.makedirs("downloads", exist_ok=True)

        # Prepare requests session with cookies
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 4:
                    continue

                case_details = cols[0].text.strip()
                judge = cols[1].text.strip()
                order_date = cols[2].text.strip()

                # PDF download
                pdf_url = None
                try:
                    pdf_btn = cols[3].find_element(By.XPATH, ".//a[contains(@href,'.pdf')]")
                    pdf_url = pdf_btn.get_attribute("href")
                except:
                    pass

                pdf_name = re.sub(r'[\\/*?:"<>|]', "_", f"{case_details}_{order_date}.pdf")
                pdf_path = os.path.join("downloads", pdf_name)

                if pdf_url and not os.path.exists(pdf_path):
                    r = session.get(pdf_url, stream=True)
                    with open(pdf_path, "wb") as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)

                data.append([case_details, judge, order_date, pdf_name])
            except Exception as e:
                print(f"Error processing row: {e}")
                continue

        # Save CSV
        df = pd.DataFrame(data, columns=["Case Details", "Hon'ble Justice", "Order/Judgement Date", "pdf_name"])
        df.to_csv("judgments_master.csv", index=False)
        print("✅ Done. Judgments saved in judgments_master.csv and PDFs in downloads/")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_rajasthan_hc(last_n_days=10, reportable="YES", headless=False)
