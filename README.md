# Matchup-results
## 說明
利用LMS八支隊伍的成績計算接下來12場比賽的勝負結果，並繪製成圖表。原先的程式使用了seaborn模組來進行繪製，並透過條件判斷計算4096種對戰結果。
## To do list
1. 重新編寫匯入變數以及原先戰績匯入方式，希望能避免使用到Json檔，Json檔當初只是為了練習讀取而使用。
2. 重新編寫代碼，並且刪除不會使用到的變數，加入代碼說明，改掉使用Dataframe進行戰績判斷的方式，改以list實現
3. 加入若為BO1之比賽之條件判斷，BO3大分小分判斷機制保留
4. 加入Multiple processing模組，觀察能否提升速度
5. 改以Matplotlib模組繪製圖表，盡力做到變數控制
