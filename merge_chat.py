import discord
import webbrowser
from selenium import webdriver
import socket
import threading
import json
import time
import requests

import socket
import subprocess
from selenium.webdriver.support.ui import WebDriverWait
import configparser
import codecs

# https://discordapp.com/developers/applications/645192983490330657/oauth
# https://discordapp.com/api/oauth2/authorize?client_id=645192983490330657&permissions=0&scope=bot

# todo: 寫 Error Log 檔

# ======================================================
# 初始化設定
# ======================================================
config = configparser.ConfigParser()
config.read_file(codecs.open('conf.ini', 'r', 'UTF-8'))
# 初始 FB 登入用的睡眠設定
sleep_time = int(config['process_variables']['sleep_time'])
# 重載 FB 聊天室的頻率設定
reload_fb_chatbox_times = int(config['process_variables']['reload_fb_chatbox_times'])
# 會常常用到的常數設定
discord_channel_id = config['env']['discord_channel_id']
discord_author_id = config['env']['discord_author_id']
# FB 的神奇特性
facebook_magic_number = 4
# 常數設定
message_from_discord = 0
message_from_twitch = 1
message_from_FB = 2

hostname = socket.gethostname()
address = socket.gethostbyname(hostname)
address = '127.0.0.1'
print('IP: ' + str(address))

proc = subprocess.Popen('php -S {}:8000'.format(address), bufsize=0)
# proc.kill()
# proc.communicate()

post_data = {"op_code": "add_message"}
api_url = 'http://{}:8000/'.format(address)
requests_object = requests.Session()

lock = threading.Lock()
def write_message (nick_name, message, source):
    message = message.replace("'", '"')
    print (message)
    lock.acquire ()
    post_data['data'] = [nick_name, message, source]
    post_data['data'] = json.dumps(post_data['data'])
    req = requests_object.post(api_url, data=post_data)
    post_data['data'] = None
    if req.status_code != 200:
        print ('post fail')
    print (req.text)
    lock.release ()

# ======================================================
# FB 擷取聊天室訊息
# ======================================================
# 直衝網頁然後手動登入再手動切回來
# fb_driver = webdriver.Chrome (config['env']['webdrive_path'])
fb_driver = webdriver.Firefox (executable_path=config['env']['webdrive_path'])

# fb_driver = webdriver.Firefox (executable_path='D:/Kai/tool/Drive/geckodriver.exe')
fb_driver.implicitly_wait(sleep_time)
fb_driver.get ('https://www.facebook.com/')
fb_driver.implicitly_wait(sleep_time)
live_url = fb_driver.find_elements_by_xpath("//input[@name='email']")
fb_driver.find_element_by_xpath("//input[@name='email']").send_keys(config['account']['email'])
fb_driver.find_element_by_xpath("//input[@name='pass']").send_keys(config['account']['password'])
fb_driver.implicitly_wait(sleep_time)
fb_driver.find_element_by_id ('loginbutton').click()
fb_driver.implicitly_wait(sleep_time)
fb_driver.get ('https://www.facebook.com/pg/{}/videos/?ref=page_internal'.format(config['env']['connect_facebook_channel']))
fb_driver.implicitly_wait(sleep_time)
# https://www.facebook.com/m3ep0414/videos/486830018689861
# https://www.facebook.com/m3ep0414/videos/486830018689861/
for live_url_item in fb_driver.find_elements_by_xpath("//*[@href and @aria-label and @id and @data-onclick and @data-video-channel-id]"):
    live_url = live_url_item.get_attribute('href')
    if live_url.find('?type=1') == -1:
        break
live_url_item.click()
# fb_driver.get (live_url)

def search_old_message_in_new_message_index (last_message_list, message_list):
    start_index = 0
    match_num = 0
    new_message_num = len (message_list)
    if len (last_message_list) >= new_message_num:
        # 用新第一個 開始比對各個舊資料，有 Match 到就開始繼續 Match 新資料
        for last_index in range (len (last_message_list)):
            match_num = 0
            if last_message_list[last_index] != message_list[0]:
                continue
            start_index = last_index
            for message_index in range (new_message_num):
                if message_list[message_index] == last_message_list[last_index+message_index]:
                    match_num = match_num + 1
                if match_num >= (new_message_num / 2):
                    return start_index
        print ('No over 1/2 string match')
    return start_index

def start_parser_facebook_chat (fb_driver):
    # todo: FB 聊天室最大訊息量只有 100 (待多次驗證)
    last_message_list = []
    while True:
        time.sleep(reload_fb_chatbox_times)
        # fb_driver.refresh()
        real_message_list = []
        real_nickname_list = []
        message_list = fb_driver.find_elements_by_class_name ('UFICommentBody')
        message_nickname_list = fb_driver.find_elements_by_class_name ('UFICommentActorName')
        # 發生錯誤代表 頁面剛好被刷新
        for index in range (len (message_list)):
            try:
                real_message_list.append (message_list[index].text)
                real_nickname_list.append (message_nickname_list[index].text)
            except:
                print('element too old already lose')
        
        print (real_message_list)
        message_list = real_message_list.copy ()
        # 檢查頭 4 個和尾 4 個如果一致就排除頭 4 個 (FB的神奇特性)
        is_remove = 0
        for index in range (facebook_magic_number):
            if message_list[index] == message_list[-1-index] or message_list[index] == '':
                is_remove = is_remove + 1
        if is_remove == facebook_magic_number:
            for index in range (is_remove):
                message_list.pop (0)
                real_nickname_list.pop (0)
        
        start_index = search_old_message_in_new_message_index (last_message_list, message_list)
        last_message_list = last_message_list[start_index:len (last_message_list)]
        # 拋棄後長度一致就不做
        if len(last_message_list) == len(message_list):
            print ('len same')
            continue
        # 印出訊息
        for index in range(len(last_message_list), len(message_list)):
            message = message_list[index]
            write_message (real_nickname_list[index], message, message_from_FB)
            print ('{}:{}'.format (real_nickname_list[index], message))
        last_message_list = message_list.copy ()

# ======================================================
# Discord 擷取聊天室訊息
# ======================================================
# 由 discord 提供 module 產生 class 並修改監聽事件
bot_client = discord.Client()
# 當成功登入時 印出準備完成，可供測試
@bot_client.event
async def on_ready ():
    print ('Bot 已登入，可輸入訊息測試')
    # channel = bot_client.get_channel (645193836062310413)
    # print (channel)

# 收到訊息時，確認訊息來源頻道
@bot_client.event
async def on_message (message):
    # 不是目標來源的訊息略過
    # if message.channel.id != 645193836062310413:
    #     return
    if message.channel.id != discord_channel_id:
        return
    
    # 確認訊息
    text = message.content
    # 訊息若為關閉 Bot 且來源為指定使用者
    if text == '!clean_token' and message.author.id == discord_author_id:
        clean_data = {'data':None, "op_code": 'clean_session'}
        req = requests_object.post(api_url, data=clean_data)
        if req.status_code != 200:
            print ('clean_token fail')
        print (req.text)
        return
    if text == '!close_bot' and message.author.id == discord_author_id:
        print ('接收到關閉指令 現在離開')
        await bot_client.close()
    write_message (message.author.name, text, message_from_discord)
# 開始執行

# ======================================================
# Twitch 擷取聊天室訊息
# ======================================================

def start_twitch_bot ():
    server = 'irc.chat.twitch.tv'
    port = 6667
    nickname = config['env']['twitch_nickname']
    token = config['env']['twitch_token']
    channel = '#{}'.format(config['env']['connect_twitch_channel'])

    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS {token}\r\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\r\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\r\n".encode('utf-8'))
    sock.send(f"CAP REQ :twitch.tv/tags\r\n".encode('utf-8'))

    send_message_title = f'PRIVMSG {channel} :'
    message_title_len = len(send_message_title)
    find_nickname_str = ';display-name='
    find_nickname_str_len = len(find_nickname_str)

    find_account_str = 'user-type= :'
    find_account_str_len = len(find_account_str)
    
    message_end_str = "\r\n"
    try:
        while True:
            display_name_start_index = -1
            display_name_end_index = -1
            resp = sock.recv(2048).decode('utf-8')
            # print (resp)
            # 是心跳包就回復
            if resp.startswith('PING'):
                # sock.send("PONG :tmi.twitch.tv\n".encode('utf-8'))
                sock.send("PONG\n".encode('utf-8'))
            # 長度奇怪，忽略
            elif len(resp) <= 0:
                continue
            # 
            message = resp.find (send_message_title)
            if message == -1:
                continue
            display_name_start_index = resp.find (find_nickname_str) + find_nickname_str_len
            display_name_end_index = resp.find (';', display_name_start_index)
            display_name = resp[display_name_start_index:display_name_end_index]
            if len (display_name) <= 0:
                display_name = resp[find_account_str_len+find_account_str_len:resp.find ('!')]
            end_index = resp.find (message_end_str)
            message = resp[message+message_title_len:end_index]
            write_message (display_name, message, message_from_twitch)

    except KeyboardInterrupt:
        sock.close()
        exit()

# ======================================================
# 整合處
# ======================================================

discord_bot = threading.Thread(target = bot_client.run, args = (config['env']['discord_bot_token'],) )
discord_bot.start ()
twitch_bot = threading.Thread(target = start_twitch_bot, args = ())
twitch_bot.start ()
facebook_chat_parser = threading.Thread(target = start_parser_facebook_chat, args = (fb_driver,))
facebook_chat_parser.start ()
