## GBL_CPU_LOADING

# USER
For User's information

------

## § 1. Brief
1. 

------

## § 2. Hardware Diagram
1. N/A

------

## § 3. Specification
1. TBD

------

## § 4. Limitation
1. TBD

------

## § 5. Porting
1. 加入header flie:#include "cpu_loading.h"
2. 宣告靜態變數: static struct cpu_loading cl;
3. 在該模組的init funtion加入本模組初始化函數，並輸入模組名稱, 需參考宏NAME_SIZE: 
   cpu_loading_init(&cl, "module_name");
4. 在該模組的loop function的active區的第一行加入計數函數:
   cpu_loading_start(&cl, gbl_uclocker());
5. 在該模組的loop function的active區的第二行加入計數函數:
   cpu_loading_end(&cl, gbl_uclocker());

------

## § 6. 打樁/相依
1. TBD

------

## § 7. Test Method
1. 上電後，先下cpu reset, 再下cpu info即可得到cpu loading和各個調用方的loop參數
2. 使用pc tool送uds, cmde command增加loading，再下一次cpu info，cpu loading(max)將會增加

------

## § 8. Configuration
1. TBD

------

# DEVELOPER
For Developer's information

------

## § 1. TODO
1. None

------

## § 2. Class View
1. TBD

------

## § 3. Input / Output
1. TBD

------

## § 4. Dynamic View or Flow Chart
1. TBD

------

## § 5. Detail Design
1. 如果先在本模組宣告特定數量的結構變數陣列，在使用上，本模組就需依據被調用的數量再調整參數，數量才不會太少無法調用，或太多浪費記憶體空間。如何改善呢?可以將結構變數由調用方宣告，如同物件導向的概念，在使用時調用方需先建立本模組的實體，這樣即使調用方的數量有增減，皆不需要修改本模組。
2. 在調用方加入本模組的init function，並以調用方的模組名稱和預期週期作為輸入參數。模組名稱的長度限制為宏定義，若調用方使用的模組名稱超過長度限制只會被截斷，不會造成錯誤。init function同時也會建立鏈結串列，目的是為了遍歷各個調用方的結構變數，才能計算cpu loading。
3. cpu_loading_start和cpu_loading_end的參數在各個調用方調用時皆相同，不會因為不同調用方而需要輸入不同參數。
4. 本模組為開發時期的效能評估，在release時即可關閉，如果在其他調用模組裡寫一堆#ifdef/#endif來當開關，會降低可讀性，因此將開關寫在自身模組的header裡，當CPU_LOADING_ENABLE為0時，四個宏被定義成空宏，不會佔用flash空間
5. 在運行時，需先下command "cpu reset"將參數重置，否則max_period將會不準確。
6. 調用方需使用32bit的gbl_uclocker(), 即4295秒之後才會溢位，故本模組在計算時，未考慮timer溢位

@startuml

title Loop

<style>
timingDiagram {
  .red {
    LineColor red
  }
  .green {
    LineColor green
  }
}
</style>

robust "loop" as loop <<red>>
loop has active,inactive

@0
loop is active
@1000
loop is inactive
@5000
loop is active
@6000
loop is inactive
@10000
loop is active
@11000
loop is inactive

@enduml
