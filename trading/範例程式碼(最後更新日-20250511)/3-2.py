import requests
from bs4 import BeautifulSoup

# 取得reponse
headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0' }
req=requests.get('https://fubon-ebrokerdj.fbs.com.tw/z/zg/zg_A_0_5.djhtm',
                 headers = headers)
# 取得網頁原始碼文字
html=req.text
# 將網頁原始碼轉為Beautiful Soup
soup=BeautifulSoup(html,'html.parser')
# 取出所有的商品欄位
product=[ i.text.strip() for i in soup.find_all('td',class_='t3t1')]
# 顯示
print(product)


