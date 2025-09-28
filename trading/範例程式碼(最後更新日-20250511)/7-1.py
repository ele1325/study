import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import csv, random, os

# 切換工作路徑（請自行調整）
os.chdir('./')

# 定義商品名稱
prod = '0050'

# 建立CSV並寫入標題列
with open(f'{prod}_shareHolder.csv', "w", encoding='utf-8-sig', newline='') as file:
    file.write("日期, 證券代碼, 持股分級, 持股數量分級, 人數, 股數, 占集保庫存數比例% \n")

# 指定 ChromeDriver 路徑
chrome_driver_path = r"chromedriver.exe"
service = Service(executable_path=chrome_driver_path)

# 設定 Chrome 選項（視需要開啟無頭模式）
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')  # 無頭模式（如需隱藏瀏覽器畫面則取消註解）
# chrome_options.add_argument('--disable-gpu')

# 啟動瀏覽器
browser = webdriver.Chrome(service=service, options=chrome_options)

# 進入查詢網址
url = "https://www.tdcc.com.tw/portal/zh/smWeb/qryStock"
browser.get(url)
time.sleep(3)

# 進行1~50周的股權分散查詢
for i in range(1, 51):
    try:
        # 選擇指定日期
        select_1 = Select(browser.find_element(By.NAME, "scaDate"))
        select_1.select_by_index(i)
        time.sleep(1)

        # 輸入股票代碼
        browser.find_element(By.ID, "StockNo").clear()
        browser.find_element(By.ID, "StockNo").send_keys(prod)
        time.sleep(1)

        # 點擊查詢按鈕
        browser.find_element(By.XPATH, "//tr[4]//td[1]//input[1]").click()
        time.sleep(1)

        # 擷取網頁原始碼
        html_file = browser.page_source
        soup = bs(html_file, "lxml")

        # 抓取資料日期
        html_date = soup.find("span", class_="font").text.split('：')[1]
        html_date = html_date.replace('年', '/').replace('月', '/').replace('日', '')
        print(f"擷取日期：{html_date}")

        # 抓取股東分級資料表
        tbody = soup.find("table", class_="table").find("tbody").find_all("tr")

        # 寫入每一筆資料到 CSV
        with open(f'{prod}_shareHolder.csv', "a", encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            for tr in tbody:
                tds = [td.text.strip() for td in tr.find_all("td")]
                writer.writerow([html_date, prod] + tds)

        # 隨機休息 5-10 秒，避免被封鎖
        time.sleep(random.randint(5, 10))

    except Exception as e:
        print(f"[錯誤] 第 {i} 筆資料擷取失敗：{e}")

# 結束後關閉瀏覽器
browser.quit()
