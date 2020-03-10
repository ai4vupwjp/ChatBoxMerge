###### tags `LiveChatMerge` `FB` `Twitch` `Discord`

# 聊天室整合程式

## 目錄
[TOC]

## 簡介
此程式碼是開源的，即所有程式碼免費開放任何人下載使用，暫不以營利為目的，僅供學習使用，也因此維護更新及安全性都是隨興而起，由於撰寫者是新手因此也歡迎指點迷津。

此程式用途在於整合各實況平台的聊天室內容為唯一一個聊天室，理論上不影響實況平台的觀看數及互動數。

## 前置作業

### Twitch

此為 Twitch 的前置作業，如不使用可以忽略。

#### Token

Twitch 該 API 是需要透過他提供的一項 **憑證(Token)** 獲得授權才允許使用，也就是所謂 Oauth (開放授權) 屬於安全性較好的行為，可以確保該操作本身是出於本人意願，而本軟體不主動提供 Token 的產生，因此如需獲得 Token，可以透過以下網站：
https://www.twitchapps.com/tmi/
> 此網站亦在官方有推薦使用，可參考該網址
https://dev.twitch.tv/docs/irc/guide/#connecting-to-twitch-irc
的 Twitch Chat OAuth Password Generator 關鍵字

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
![範例圖12](https://i.imgur.com/z99e3ag.png)

&ensp;

登入用憑證 可以至剛剛到訪過的 Bot 標籤 點選 copy 複製貼上即可。
&ensp;

特殊權限人員 ID 只要在右側列表按右鍵即會出現 複製ID 選項，目前此選項尚未做特殊功能，因此可以忽略。

這三項數值，僅需要在等號右邊打上內容即可。

### FB

此為 FB 實況的前置作業，如不使用可以忽略。


#### 申請應用程式

![範例圖13](https://i.imgur.com/bwMSPw0.png)
&ensp;

登入FB後，左側會有管理應用程式，點進去後會看到上圖的畫面，點選新增應用程式，並隨意取名。
&ensp;

![範例圖14](https://i.imgur.com/r5q0A7y.png)
&ensp;


點選左側的主控版標籤，之後注意此數上方的應用程式編號，先記錄下來等等會用到。
接著直接往下滾動選取 Facebook 登入右下角的設定
&ensp;
![範例圖15](https://i.imgur.com/1G9dNPT.png)
&ensp;

看到此畫面後使用相同配置即可，並在重新導向登入頁輸入以下網址：
https://www.facebook.com/connect/login_success.html
此網址是 FB 指定若是使用桌面應用程式等其他方式登入時，必須輸入的網址

[可參考此處 FB 說明](https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow)

之後點選以下網址
https://developers.facebook.com/tools/explorer/
進入 FB 開發者用的圖形 API 測試工具

![範例圖16](https://i.imgur.com/1lCzHhW.png)
&ensp;

進入後右側可選取要使用的應用程式與用戶或粉絲專業及權限列表。

若是屬於個人實況則選 **用戶權杖**，若為粉絲專業實況則選 **取得粉絲專業存取權杖**。
選好對象後，再點選，**新增權限** 來新增需要的權限。

![範例圖17](https://i.imgur.com/XzlLGx3.png)
&ensp;

點選新增權限後，選取 User Data Permissions

![範例圖18](https://i.imgur.com/2J9Kwq2.png)
&ensp;

User Data Permissions 是一個大項目，再選取其中的細項 user_videos

![範例圖19](https://i.imgur.com/EXfULwh.png)
&ensp;

選完之後點 Get Access Token 就完成了。

權限會依 **實況是否屬於特定用戶 或 測試用僅個人可見的實況，而有所不同**，此處僅使用最低需求的權限，(即面向所有觀眾的)作為範例，如需其他用途的實況...自己想辦法或是都選吧 XD

該項 user_videos 會要求授權，使本應用程式能用存取

1. 該用戶上傳過的影片
2. 打卡資訊?
3. 收到的回應(可能包含心情及留言等...)

如圖:

![範例圖20](https://i.imgur.com/HPmlpZm.png)


#### 設定檔

![範例圖21](https://i.imgur.com/B16B0s2.png)

接下來需要來設定所謂的設定檔，本軟體會依照設定檔的內容做FB的驗證授權登入並抓取實況中頻道的即時聊天內容。

1. 應用程式 ID app_id
2. 防止跨網站偽造的 Token state_param

應用程式ID 在上述處有說明需記錄下來的。
防止跨網站偽造的 Token 則是用來防止有其他非使用者本人發出請求 (也就是所謂 [CSRF(跨站要求偽造)](https://hackmd.io/3xrQ2n05QSmNV0tOzdqBpg?view)) 的東西，此處應該是可以自行隨意填寫自行獨有的內容。

### 本軟體的前置作業

僅需達成能執行 php 的環境變數即可。

## 使用說明

待補。

## 注意事項
開發過程尚未完成或者能力不足無法完成的項目及隱患。

1. 本程式碼 使用 php 及 python 透過該程式語言 Simple httpserver 的方式完成，其中 php 使用的方法採用每次訪問視為同一個 Session 此方法未確認過安全性及可靠度(使用 127.0.0.1 的方式是否存在隱患尚未知曉)。

2. 面向 FB 的方法未確認過流量限制(FB 官方規定，申請的應用程式時段內可以訪問 FB 的次數有所限制)

3. FB 使用之方法未確認過粉絲專頁的開台方式是否可以使用。

4. 整體未進行過壓力測試，尚無確認在長時間開台及高頻率聊天下的程序效率與記憶體狀況。


## 參考資料
[FaceBook developer](https://developers.facebook.com/)
[Twitch developer about ChatBot & IRC](https://dev.twitch.tv/docs/irc/guide/#connecting-to-twitch-irc)
