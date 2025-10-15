# 載入必要套件
from Data import getPriceAndShareHolder
from BackTest import ChartTrade,Performance
import pandas as pd
import mplfinance as mpf

# 取得回測資料
prod='0050'
data=getPriceAndShareHolder(prod,'2007-01-01','2025-10-14')

# 30張持有以下稱為散戶
data['minority']=data['1']+data['2']+data['3']+data['4']+data['5']
# 400張持有以上稱為大股東
data['major']=data['12']+data['13']+data['14']+data['15']

# 繪製副圖
addp=[]
# 小股東曲線
addp.append(mpf.make_addplot(data['minority'],panel=1,secondary_y=False,color='r'))
# 大股東曲線
addp.append(mpf.make_addplot(data['major'],panel=1,secondary_y=False,color='y'))

# 繪製K線圖與交易明細
ChartTrade(data,addp=addp,v_enable=False)


