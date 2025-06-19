# scraper.py
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def init_driver():
    options = webdriver.EdgeOptions()
    options.add_argument('disable-gpu')
    options.add_argument('window-size=500,1080')
    return webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

def wait_for_page_load(driver):
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

def get_cert_links(driver):
    ul_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="content-browser-container"]/div/div/div[2]/ul'))
    )
    li_elements = ul_element.find_elements(By.XPATH, './li/article/div[1]/a')
    return [link.get_attribute("href") for link in li_elements]

# 模組
def click_modules(driver):
    modules_data = []
    module_blocks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-bi-name="module"]'))
    )

    for idx, module in enumerate(module_blocks, start=1):
        print(f"            🔗 第 {idx} 個模組：")
        try:
            #抓模組標題
            try:  # 優先用 a 抓 title 和 href
                link_elem = module.find_element(By.CSS_SELECTOR, 'a.font-weight-semibold')
                link_text = link_elem.text.strip()
                link_href = link_elem.get_attribute('href')
            except:  # fallback：用 h3 抓 title，並從祖先找 <a>
                link_elem = module.find_element(By.CSS_SELECTOR, 'h3.font-size-h6')
                link_text = link_elem.text.strip()
                parent_a = link_elem.find_element(By.XPATH, './ancestor::a[1]')
                link_href = parent_a.get_attribute('href')
            
            # 抓模組敘述
            try: 
                summary_div = module.find_element(By.CSS_SELECTOR, '.module-summary')

                # 移除內部 class="alert" 的元素
                alerts = summary_div.find_elements(By.CSS_SELECTOR, '.alert')
                for alert in alerts:
                    driver.execute_script("arguments[0].remove();", alert)
                desc_text = summary_div.get_attribute('textContent').strip()
            except Exception as e:
                desc_text = "(❌ 無法取得敘述)"
            
            #print(f"        📘 標題：{link_text}")
            #print(f"        🌐 連結：{link_href}")
            #print(f"        📝 敘述：{desc_text}")

            modules_data.append({
                'title': link_text,
                'url': link_href,
                'description': desc_text
            })

        except Exception as e:  
            print(f"❌ 第 {idx} 個模組擷取失敗：{e}")
    return modules_data


# 課程 
def process_courses(driver, db, cert_title, cert_url):
    try:
        # 抓認證介紹
        try:
                cert_description_element = driver.find_element(By.XPATH, '//*[@id="certification-hero"]/div/div[2]/p[2]')
                cert_description = cert_description_element.text.strip()
        except:
                cert_description = "❌（找不到介紹）"
        print(f"   認證介紹：{cert_description}")

        course_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//section[6]//ul/li/article/div[2]/ul[2]//a'))
        )

        # 爬課程
        for idx, link in enumerate(course_links, start=1):
            course_title = link.text.strip()
            course_url = link.get_attribute("href")
            print(f"    👉 課程 {idx}：{course_title} ({course_url})")

            driver.execute_script("window.open(arguments[0]);", course_url)
            driver.switch_to.window(driver.window_handles[-1])
            wait_for_page_load(driver)

            # 爬課程介紹
            course_description = "❌（找不到課程介紹）"
            for i in [4, 5, 6]:
                try:
                    xpath = f'//*[@id="main"]/div[3]/div[1]/div/div/div/div/div[{i}]/p'
                    description_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    course_description = description_element.text.strip()
                    break  # 找到了就退出迴圈
                except:
                    continue
            #print(f"      課程介紹：{course_description}")

            modules = click_modules(driver)

            # 將所有資訊送資料庫
            db.insert_course_structure(
                certification_title=cert_title,
                certification_url=cert_url,
                certification_description=cert_description,
                course_title=course_title,
                course_url=course_url,
                course_description=course_description,
                modules=modules
)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

    except Exception as e:
        print(f"    ❌ 課程處理失敗：{e}")