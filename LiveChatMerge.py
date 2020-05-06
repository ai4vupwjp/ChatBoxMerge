import discord
import socket
import threading
import json
import time
import requests

import subprocess
import os

import configparser
import codecs

import webview
from urllib.parse import urlparse
from urllib.parse import parse_qs

import traceback
import math

# https://discordapp.com/developers/applications/645192983490330657/oauth
# https://discordapp.com/api/oauth2/authorize?client_id=645192983490330657&permissions=0&scope=bot
# https://developers.facebook.com/docs/graph-api/reference/user/live_videos/?locale=zh_TW
# todo: 寫 Error Log 檔

# ======================================================
# 初始化設定
# ======================================================
config = configparser.ConfigParser()
config.read_file(codecs.open('conf.ini', 'r', 'UTF-8'))
# 初始 FB 登入用的睡眠設定
sleep_time = int(config['process_variables']['sleep_time'])
# 會常常用到的常數設定
discord_channel_id = config['env']['discord_channel_id']
discord_author_id = config['env']['discord_author_id']
# 啟動設定
is_merge_twitch = int(config['process_variables']['is_merge_twitch'])
is_merge_facebook = int(config['process_variables']['is_merge_facebook'])
is_merge_discord = int(config['process_variables']['is_merge_discord'])
is_write_log = int(config['process_variables']['is_write_log'])
is_remove_old_session_file = int(config['process_variables']['is_remove_old_session_file'])
# 常數設定
message_from_discord = 0
message_from_twitch = 1
message_from_FB = 2

hostname = socket.gethostname()
address = socket.gethostbyname(hostname)
address = '127.0.0.1'
port = int(config['process_variables']['port'])
print('IP: ' + str(address))

if is_remove_old_session_file == 1 and os.path.isfile('./tmp/sess_b9jc4kekq6idnvsjdo7sf57t3f'):
    os.remove('./tmp/sess_b9jc4kekq6idnvsjdo7sf57t3f')

proc = subprocess.Popen('php -S {}:{}'.format(address, port), bufsize=0)
# proc.kill()
# proc.communicate()

post_data = {"op_code": "add_message"}
api_url = 'http://{}:{}/'.format(address, port)
requests_object = requests.Session()

lock = threading.Lock()
def write_message (nick_name, message, source):
    message = message.replace("'", '"')
    lock.acquire ()
    post_data['data'] = [nick_name, message, source]
    post_data['data'] = json.dumps(post_data['data'])
    req = requests_object.post(api_url, data=post_data)
    post_data['data'] = None
    if req.status_code != 200:
        print ('post fail')
    # print (req.text)
    lock.release ()

def print_log(message):
    if is_write_log == 0:
        return
    print(message)

# ======================================================
# Discord 擷取聊天室訊息
# ======================================================
# 由 discord 提供 module 產生 class 並修改監聽事件
bot_client = discord.Client()
# 當成功登入時 印出準備完成，可供測試
@bot_client.event
async def on_ready ():
    print ('Discord Bot 已登入 開始擷取聊天室訊息 可輸入訊息測試')
    # channel = bot_client.get_channel (645193836062310413)
    # print (channel)

# 收到訊息時，確認訊息來源頻道
@bot_client.event
async def on_message (message):
    # 不是目標來源的訊息略過
    if message.channel.id != int(discord_channel_id):
        print_log('訊息來源頻道ID: {} 與預期頻道ID: {} 不同'.format(message.channel.id, discord_channel_id))
        return
    
    # 確認訊息
    text = message.content
    # 訊息若為關閉 Bot 且來源為指定使用者
    if text == '!clean_token' and message.author.id == discord_author_id:
        clean_data = {'data':'', "op_code": 'clean_session'}
        req = requests_object.post(api_url, data=clean_data)
        if req.status_code != 200:
            print_log ('請求清除聊天室失敗')
        print_log('請求清除聊天室訊息, 收到回復')
        print_log (req.text)
        return
    if text == '!close_bot' and message.author.id == discord_author_id:
        print_log ('接收到關閉指令，關閉 Bot')
        await bot_client.close()
    write_message (message.author.name, text, message_from_discord)
    print_log ('{}: {}'.format (message.author.name, text))

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
            print_log('收到 Twitch 訊息')
            print_log(resp)
            # 是心跳包就回復
            if resp.startswith('PING'):
                # sock.send("PONG :tmi.twitch.tv\n".encode('utf-8'))
                sock.send("PONG\n".encode('utf-8'))
            # 長度奇怪，忽略
            elif len(resp) <= 0:
                print_log ('訊息內容長度有問題 忽略本次訊息')
                retry_times = 1
                print('等候 {} 秒後重試'.format(math.pow(2, retry_times)))
                time.sleep(math.pow(2, retry_times))
                continue
            # 
            message = resp.find (send_message_title)
            if message == -1:
                print_log ('訊息中未發現 目標頻道名稱 忽略本次訊息')
                retry_times = 1
                print('等候 {} 秒後重試'.format(math.pow(2, retry_times)))
                time.sleep(math.pow(2, retry_times))
                continue
            display_name_start_index = resp.find (find_nickname_str) + find_nickname_str_len
            display_name_end_index = resp.find (';', display_name_start_index)
            display_name = resp[display_name_start_index:display_name_end_index]
            if len (display_name) <= 0:
                display_name = resp[find_account_str_len+find_account_str_len:resp.find ('!')]
            end_index = resp.find (message_end_str)
            message = resp[message+message_title_len:end_index]
            write_message (display_name, message, message_from_twitch)
            print_log ('{}: {}'.format (display_name, message))

    except KeyboardInterrupt:
        sock.close()
        exit()

app_id = config['env']['app_id']
redirect_uri = config['env']['redirect_uri']
state_param = config['env']['state_param']
state_param = '{st=state123abc,ds=123456789}'
fb_webview = None

def start_parser_facebook_chat(fb_webview):
    time.sleep(int(config['process_variables']['sleep_time']))
    fb_url = fb_webview.get_current_url()
    fb_webview.destroy()
    print_log('獲得 FB 登入的 URL')
    print_log(fb_url)
    fb_url = urlparse(fb_url)
    fb_url = parse_qs(fb_url.fragment)
    print_log('解析後呈現')
    print_log(fb_url)
    access_token = fb_url['access_token'].pop()
    print_log('權杖Token (Access_token)')
    print_log(access_token)
    req = requests.get(f'https://graph.facebook.com/v6.0/me?fields=id,name&access_token={access_token}')
    if req.status_code > 200:
        print_log ('請求 FB 個人 ID 失敗')
        print_log(req)
        print_log(req.text)
        print('請求個人 ID 失敗 FB 擷取失敗')
        return
    is_facebook_page = int(config['env']['is_facebook_page'])
    me = json.loads(req.text)
    user_id = me['id']
    if is_facebook_page == 1:
        print_log ('請求粉專 ID 中')
        req = requests.get(f'https://graph.facebook.com/v6.0/{user_id}/accounts?access_token={access_token}')
        print_log('Test')
        if req.status_code > 200:
            print_log ('請求 FB 粉專 ID 失敗')
            print_log(req)
            print_log(req.text)
            print('請求粉專 ID 失敗 FB 擷取失敗')
            return
        print_log(req.text)
        me = json.loads(req.text)
        user_id = me['data'].pop(0)['id']
    retry_times = 0
    while True:
        req = requests.get(f'https://graph.facebook.com/v6.0/{user_id}/live_videos?access_token={access_token}')
        if req.status_code > 200:
            print_log ('請求 FB 粉專 ID 失敗')
            print_log(req)
            print_log(req.text)
            print('請求影片內容失敗 FB 擷取失敗')
            return
        print_log('獲得影片內容')
        print_log(req.text)
        live_video_node = json.loads(req.text)
        live_video_id = None
        # 這段程式碼待驗證
        for item in live_video_node['data']:
            if item['status'] == 'LIVE':
                live_video_id = item['id']
                break
        print_log ('找尋到的影片 ID')
        print_log(live_video_id)
        if live_video_id != None:
            break
        retry_times = retry_times + 1
        print('等候 {} 秒後重試'.format(math.pow(2, retry_times)))
        time.sleep(math.pow(2, retry_times))
        print('未找到正在實況中的影片內容，擷取失敗')
    
    req = requests.get(f'https://streaming-graph.facebook.com/{live_video_id}/live_comments?access_token={access_token}&fields=from,message', stream=True)
    print('開始擷取 FB 聊天室 可輸入訊息測試')
    print_log('開始嘗試擷取 FB 聊天室')
    for line in req.iter_lines():
        line = line.decode('utf-8')
        line = line[6:]
        if line:
            line = json.loads(line)
            write_message(line['from']['name'], line['message'], message_from_FB)
            print_log ('{}: {}'.format (line['from']['name'], line['message']))
        else:
            print_log('FB ping')
    

# ======================================================
# 整合處
# ======================================================
if is_merge_discord == 1:
    discord_bot = threading.Thread(target = bot_client.run, args = (config['env']['discord_bot_token'],) )
    discord_bot.start ()
if is_merge_twitch == 1:
    twitch_bot = threading.Thread(target = start_twitch_bot, args = ())
    twitch_bot.start ()
if is_merge_facebook == 1:
    login_url = f'https://www.facebook.com/v6.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&state={state_param}&response_type=token,granted_scopes'
    fb_webview = webview.create_window('Webview', login_url)
    facebook_chat_parser = threading.Thread(target = start_parser_facebook_chat, args = (fb_webview,))
    facebook_chat_parser.start ()
    webview.start()

