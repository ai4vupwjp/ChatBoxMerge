import discord
import socket
import threading
import json
import time
import requests

import subprocess

import configparser
import codecs

import webview
from urllib.parse import urlparse
from urllib.parse import parse_qs

import traceback

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
    lock.acquire ()
    post_data['data'] = [nick_name, message, source]
    post_data['data'] = json.dumps(post_data['data'])
    req = requests_object.post(api_url, data=post_data)
    post_data['data'] = None
    if req.status_code != 200:
        print ('post fail')
    # print (req.text)
    lock.release ()

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
    if message.channel.id != int(discord_channel_id):
        print(message.channel.id)
        print(discord_channel_id)
        return
    
    # 確認訊息
    text = message.content
    # 訊息若為關閉 Bot 且來源為指定使用者
    if text == '!clean_token' and message.author.id == discord_author_id:
        clean_data = {'data':'', "op_code": 'clean_session'}
        req = requests_object.post(api_url, data=clean_data)
        if req.status_code != 200:
            print ('clean_token fail')
        print (req.text)
        return
    if text == '!close_bot' and message.author.id == discord_author_id:
        print ('接收到關閉指令 現在離開')
        await bot_client.close()
    write_message (message.author.name, text, message_from_discord)
    print ('{}: {}'.format (message.author.name, text))

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
            print ('{}: {}'.format (display_name, message))

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
    print(fb_url)
    fb_url = urlparse(fb_url)
    fb_url = parse_qs(fb_url.fragment)
    print(fb_url)
    access_token = fb_url['access_token'].pop()
    print('Access_token')
    print(access_token)
    req = requests.get(f'https://graph.facebook.com/v6.0/me?fields=id,name&access_token={access_token}')
    if req.status_code > 200:
        print(req)
        print(req.text)
    is_facebook_page = int(config['env']['is_facebook_page'])
    me = json.loads(req.text)
    user_id = me['id']
    if is_facebook_page == 1:
        req = requests.get(f'https://graph.facebook.com/v6.0/{user_id}/accounts?access_token={access_token}')
        print('Test')
        print(req.text)
        me = json.loads(req.text)
        user_id = me['data'].pop(0)['id']
    req = requests.get(f'https://graph.facebook.com/v6.0/{user_id}/live_videos?access_token={access_token}')
    if req.status_code > 200:
        print(req)
        print(req.text)
    print(req.text)
    live_video_node = json.loads(req.text)
    live_video_id = None
    # 這段程式碼待驗證
    for item in live_video_node['data']:
        if item['status'] == 'LIVE':
            live_video_id = item['id']
            break
    print(live_video_id)
    # live_video_id = 2648572082037444
    
    
    req = requests.get(f'https://streaming-graph.facebook.com/{live_video_id}/live_comments?access_token={access_token}&fields=from,message', stream=True)
    for line in req.iter_lines():
        line = line.decode('utf-8')
        line = line[6:]
        if line:
            line = json.loads(line)
            print(line['from']['name'])
            print(line['message'])
            write_message(line['from']['name'], line['message'], message_from_FB)
        else:
            print('FB ping')
    



# ======================================================
# 整合處
# ======================================================

discord_bot = threading.Thread(target = bot_client.run, args = (config['env']['discord_bot_token'],) )
discord_bot.start ()
twitch_bot = threading.Thread(target = start_twitch_bot, args = ())
twitch_bot.start ()

login_url = f'https://www.facebook.com/v6.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&state={state_param}&response_type=token,granted_scopes'
fb_webview = webview.create_window('Webview', login_url)
facebook_chat_parser = threading.Thread(target = start_parser_facebook_chat, args = (fb_webview,))
facebook_chat_parser.start ()
webview.start()