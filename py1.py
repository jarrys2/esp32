from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 讀取設定檔
def load_config(file_path):
    config = {}
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key.strip()] = value.strip()
    return config

# 載入 config.txt
config = load_config("config.txt")
your_name = config.get("name", "預設名")
your_phone = config.get("phone", "0900000000")
reservation_date = config.get("date", "2025/09/01")
adult_count = config.get("adult", "4")
child_count = "0"  # 固定為 0
target_time = config.get("time", "15:00")

# 啟動 ChromeDriver
service = Service("chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get("https://eat.tagfans.com/admin/reservation.html?o=10923")
    wait = WebDriverWait(driver, 20)

    wait.until(EC.presence_of_element_located((By.ID, "datetimepicker_item")))

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[Field="Adult"]')))
    driver.find_element(By.CSS_SELECTOR, 'input[Field="Adult"]').clear()
    driver.find_element(By.CSS_SELECTOR, 'input[Field="Adult"]').send_keys(adult_count)

    try:
        child_input = driver.find_element(By.CSS_SELECTOR, 'input[Field="Child"]')
        driver.execute_script("arguments[0].value = '';", child_input)
        child_input.send_keys(child_count)
    except Exception:
        print("⚠️ 小孩欄位無法互動，已略過")

    date_field = driver.find_element(By.ID, "datetimepicker_item")
    driver.execute_script("arguments[0].value = arguments[1];", date_field, reservation_date)
    time.sleep(2)

    wait.until(EC.presence_of_element_located((By.ID, "slots_content")))
    time.sleep(2)
    slots = driver.find_elements(By.CSS_SELECTOR, '#slots_content button:not(.disabled)')
    if not slots:
        print("❌ 沒有任何可預約時段")
        driver.quit()
        exit()

    matched_slot = None
    for btn in slots:
        if target_time in btn.text:
            matched_slot = btn
            break

    if not matched_slot:
        print(f"❌ 找不到符合「{target_time}」的可預約時段")
        driver.quit()
        exit()

    matched_slot.click()

    driver.find_element(By.ID, "showIdentityButton").click()
    wait.until(EC.presence_of_element_located((By.ID, "offcanvas-identity")))
    time.sleep(1)

    driver.find_element(By.CSS_SELECTOR, '#offcanvas-identity input[Field="Name"]').clear()
    driver.find_element(By.CSS_SELECTOR, '#offcanvas-identity input[Field="Name"]').send_keys(your_name)

    driver.find_element(By.CSS_SELECTOR, '#offcanvas-identity input[Field="Phone"]').clear()
    driver.find_element(By.CSS_SELECTOR, '#offcanvas-identity input[Field="Phone"]').send_keys(your_phone)

    driver.find_element(By.CSS_SELECTOR, '#offcanvas-identity button[onclick^="sendReservation"]').click()

    print(f"✅ 預約 {reservation_date} {target_time} 已送出！")
    time.sleep(5)

finally:
    driver.quit()
