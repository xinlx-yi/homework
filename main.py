# main.py
from scraper import init_driver, wait_for_page_load, get_cert_links, process_courses
from db_handler import DBHandler
from selenium.webdriver.common.by import By
import time

# 抓認證標題
def get_cert_title(driver):
    try:
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        print(f"   認證標題：{title}")
        return title
    except:
        print("❌ 認證標題擷取失敗")
        return "Unknown Certification"

def main():
    driver = init_driver()

    db = DBHandler(
        server='localhost',
        database='microsoft'
    )

    try:
        url = "https://learn.microsoft.com/zh-tw/credentials/browse/?credential_types=fundamentals&expanded=certification&levels=beginner"
        driver.get(url)
        wait_for_page_load(driver)

        cert_links = get_cert_links(driver)

        #for i, cert_url in enumerate(cert_links[:3], start=1):
        for i, cert_url in enumerate(cert_links, start=1):
            print(f"\n👉 開始第 {i} 個認證：{cert_url}")
            driver.get(cert_url)
            wait_for_page_load(driver)

            cert_title = get_cert_title(driver)

            process_courses(driver, db, cert_title, cert_url)

            print(f"✅ 認證 {i} 完成")
            time.sleep(2)

        db.commit()

    finally:
        db.close()
        driver.quit()

if __name__ == "__main__":
    main()
