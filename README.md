# weiqigo
A weiqi go tool. 圍棋打譜練習程式

這是一個以python+tk所寫成的小程式。可以將儲存為sgf格式的定石、詰棋作為練習。</BR>
跟一般的打譜程式有何不同：這個程式是以作死活的方式練習sgf，強調是否記住正確的著手。

## License
本程式為 MIT License ，部份程式有各自的 License ，分別為

* [sgf.py](https://github.com/jtauber/sgf)
* [board.py](https://github.com/ymgaq/Pyaq)

## 操作說明
* 選目錄：按「選目錄」鈕，選擇欲練習檔案存放的目錄，不包含子目錄。</BR>
* 滑鼠左鍵：在棋盤上按滑鼠左鍵答題，錯誤時畫面顯示X。</BR>
* 滑鼠右鍵：自由落子，供使用者自由在棋盤上下子。</BR>
* 上一題：按「上一題」鈕，切換至目錄內的上一題。</BR>
* 下一題：按「下一題」鈕，切換至目錄內的下一題。</BR>
* 是示：勾選「題示」後，下一手棋會在棋盤上顯示為灰色小點。</BR>
* 上一步：按「上一步」鈕，切換至sgf的上一手棋。</BR>
* 下一步：按「下一步」鈕，切換至sgf的下一手棋。

## sgf 格式
* sgf檔須為utf-8編碼。</BR>
* 程式讀取sgf檔案後，會在棋盤上顯示至註解為qq的那一手棋。可以在待解題的那一手棋的註解打上qq讓程式知道要顯示到哪一手。</BR>
* 註解為r的那一手棋會顯示為「正確」。</BR>
* 註解為w的那一手棋會顯示為「錯誤」。

## Todo
* 變化分支的圖形顯示
* 錯題的紀錄及重答

### 聯絡資訊
如果有任何問題或是建議，可以通過 ```riverboundry@gmail.com``` 聯繫我。
