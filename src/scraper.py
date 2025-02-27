import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup

# ✅ Configure Chrome options for Docker
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# ✅ Start WebDriver
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# ✅ Open URL
url = "https://play.google.com/store/apps/details?id=com.boc.itdiv.smartpassbook&hl=en"
driver.get(url)
time.sleep(5)

# ✅ Click "See all reviews" button
try:
    wait = WebDriverWait(driver, 10)
    button_xpath = "//button/span[contains(text(),'See all reviews')]"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))

    driver.execute_script("arguments[0].scrollIntoView();", button)
    time.sleep(2)
    driver.execute_script("arguments[0].click();", button)

    print("✅ Clicked 'See all reviews' button.")
    time.sleep(5)
except Exception as e:
    print("❌ Button click failed:", e)

# ✅ Find the review section
try:
    review_section_xpath = '//div[contains(@class, "fysCi") or contains(@class, "review-dialog-list")]'
    review_section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, review_section_xpath))
    )

    print("✅ Review section found.")
except Exception as e:
    print("❌ Failed to find review section:", e)

# ✅ Function to scroll and load more reviews
def real_scroll():
    previous_count = 0
    min_scrolls = 10  # 🔹 Ensure at least 10 scrolls happen
    max_scrolls = 100  # 🔹 Increased max scrolls

    for i in range(max_scrolls):
        # ✅ Click "More" button if available
        try:
            more_button = driver.find_element(By.XPATH, "//button[contains(text(),'More')]")
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(4)
            print("✅ Clicked 'More' button.")
        except:
            pass  # Ignore if button isn't found

        # ✅ Scroll multiple times per loop
        for _ in range(4):  # 🔹 Multiple page downs
            review_section.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

        # ✅ Count loaded reviews
        reviews = driver.find_elements(By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div/div/div/div[2]/div/div[2]/div')
        review_count = len(reviews)

        print(f"🔄 Scrolling... Reviews loaded: {review_count}")

        if review_count == previous_count and i >= min_scrolls:
            print("✅ No more new reviews. Stopping scroll.")
            break  # ✅ Stop if no new reviews load after min_scrolls
        previous_count = review_count

        time.sleep(2)  # ✅ Give time for new reviews to load

# ✅ Run smooth scrolling
real_scroll()

# ✅ Function to clean extracted text (fixes Sinhala, Tamil, and emoji issues)
def clean_text(text):
    return BeautifulSoup(text, "html.parser").get_text().strip()

# ✅ Extract and Save Reviews to CSV
def extract_reviews():
    print("📥 Extracting reviews...")

    reviews_data = []
    
    # ✅ Locate all reviews
    reviews = driver.find_elements(By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div/div/div/div[2]/div/div[2]/div')

    for i, review in enumerate(reviews, start=1):
        try:
            # ✅ Extract Name
            name = clean_text(review.find_element(By.XPATH, './/header/div[1]/div[1]/div').get_attribute("innerText"))

            # ✅ Extract Rating
            rating_element = review.find_element(By.XPATH, './/header/div[2]/div')
            rating = rating_element.get_attribute("aria-label")  # Extract rating properly

            # ✅ Extract Date
            date = clean_text(review.find_element(By.XPATH, './/header/div[2]/span').get_attribute("innerText"))

            # ✅ Extract Comment
            try:
                comment_xpath = f'//*[@id="yDmH0d"]/div[5]/div[2]/div/div/div/div/div[2]/div/div[2]/div[{i}]/div[1]'
                comment = clean_text(driver.find_element(By.XPATH, comment_xpath).get_attribute("innerText"))
            except:
                comment = "N/A"  # Fallback if comment extraction fails

            # ✅ Store data
            reviews_data.append([name, rating, date, comment])
        except Exception as e:
            print(f"❌ Error extracting review {i}:", e)

    # ✅ Generate timestamp-based filename with UTC time
    now_utc = datetime.utcnow()  # 🔹 Use UTC time
    timestamp = now_utc.strftime("%d-%m-%Y_%H-%M")  # 🔹 Format: 27-02-2025_11-41 (UTC)

    # ✅ Save to CSV (Fix Sinhala, Tamil, and Emoji encoding)
    csv_file = f"/app/data/{timestamp}-BOC_Smart_Passbook_reviews.csv"
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)  # ✅ Ensure directory exists

    with open(csv_file, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Rating", "Date", "Comment"])  # CSV Header
        writer.writerows(reviews_data)

    print(f"📁 Saved {len(reviews_data)} reviews to {csv_file}!")

# ✅ Run extraction
extract_reviews()

# ✅ Close WebDriver
driver.quit()
print("🎉 Scraping complete! Data saved.")
