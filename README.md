###### tags `LiveChatMerge` `FB` `Twitch` `Discord`

# 聊天室整合程式

## 簡介
此程式碼是開源的，即所有程式碼免費開放任何人下載使用，暫不以營利為目的，僅供學習使用，也因此維護更新及安全性都是隨興而起，由於撰寫者是新手因此也歡迎指點迷津。

此程式用途在於整合各實況平台的聊天室內容為唯一一個聊天室，理論上不影響實況平台的觀看數及互動數。

## 前置作業

### Twitch

此為 Twitch 的前置作業，如不使用可以忽略。

#### Token

Twitch 該 API 是需要透過他提供的一項 **憑證(Token)** 獲得授權才允許使用，也就是所謂 Oauth (開放授權) 屬於安全性較好的行為，可以確保該操作本身是出於本人意願，而本軟體不主動提供 Token 的產生，因此如需獲得 Token，可以透過以下網站：
https://www.twitchapps.com/tmi/
或是自行產生 Token 來使用。

#### 設定檔
![範例圖01](https://i.imgur.com/IOpIx6m.png)
接下來需要來設定所謂的設定檔，本軟體會依照設定檔的內容做登入及頻道的進入動作，也因此需要設定

1. Twitch 頻道 connect_twitch_channel
2. 剛剛申請的憑證 twitch_token
3. 申請憑證用的帳號 twitch_nickname

這三項數值，僅需要在等號右邊打上內容即可。


### Discord

雖然 Discord 並非實況平台，但是有需求就有產出，如不使用可以忽略。
本軟體是以 GitHub 上第三方庫包裝過的類做為客戶端。

#### 開發者模式
使用 Discord 整合需先將 Discord 切換至開發者模式

![範例圖02](https://i.imgur.com/ymsUYfn.png)
&ensp;
點選上圖的左下黃色框選處
&ensp;
![範例圖03](https://i.imgur.com/AdkzvQY.png)
&ensp;
再點選上圖點選左側 **外觀** 標籤，再開啟 **開發者模式** 即可完成。
&ensp;

#### 申請應用程式

Discord 屬於需要申請應用程式的方式。點選以下網址：
https://discordapp.com/developers/applications
(或自行至 Discord 官方網站，點選開發人員->開發人員入口網站亦可。)

此網站目前我點進去是英文，所以看到忽然轉成英文，也莫慌張。

![範例圖04](https://i.imgur.com/KvfcLvu.png)

&ensp;
點選右上角 New Application 
&ensp;

![範例圖05](https://i.imgur.com/TMK91k9.png)

&ensp;
並輸入你要為你的應用程式取的名稱
&ensp;

![範例圖06](https://i.imgur.com/PHqWl4N.png)
&ensp;
取名完會來到上圖這個畫面，點選左側 **Bot** 的標籤
&ensp;
![範例圖07](https://i.imgur.com/yTz7YCG.png)
&ensp;
來到上圖這個畫面後，再點右側 Add Bot，他會再次詢問你是否要執行，按是。
&ensp;
![範例圖08](https://i.imgur.com/ZVtIkEC.png)
&ensp;
完成後再次點擊左側 OAuth2 標籤，來到此頁面，將 Bot 選項勾起。
&ensp;
![範例圖09](https://i.imgur.com/8ptKN0s.png)
&ensp;
勾起後往底下滾動可以看到該 Bot 的權限，可以勾選需要的權限，目前 **不需要任何權限，所以不需要勾選任何權限。** 所以按下 Copy 複製此網頁產生的網址。
&ensp;

之後再於瀏覽器上貼上該網址，進入 Discord 的網頁並選擇你要讓 Bot 加入的頻道，完成後該名 Bot 就會被加入至該頻道。

#### 設定檔
![範例圖10](https://i.imgur.com/vCpExJo.png)

接下來需要來設定所謂的設定檔，本軟體會依照設定檔的內容做頻道的監聽及用以登入的憑證。

1. 需要監聽的頻道 ID discord_channel_id
2. 特殊權限人員 ID discord_author_id
3. 登入用憑證 discord_bot_token


![範例圖11](https://i.imgur.com/W0PXel5.png)
&ensp;
需要監聽的頻道 ID 只要有開啟開發者模式對頻道按右按即可看到 **複製ID** 的選項。
&ensp;
![範例圖12](https://i.imgur.com/QKA6d7p.png)
&ensp;
登入用憑證 可以至剛剛到訪過的 Bot 網頁點選 copy 複製貼上即可。
&ensp;

特殊權限人員 ID 只要在右側列表按右鍵即會出現 複製ID 選項，目前此選項尚未做特殊功能，因此可以忽略。

這三項數值，僅需要在等號右邊打上內容即可。

### FB

懶 待補。
