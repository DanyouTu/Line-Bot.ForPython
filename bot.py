from flask import Flask, request, render_template_string
from linebot import LineBotApi, WebhookHandler
# from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from datetime import datetime, timedelta
import json
import openai
import redis

# 初始化 Flask 應用
app = Flask(__name__)
app.secret_key = "secret_key"

# 設置 Line Bot API 和 WebhookHandler
line_bot_api = LineBotApi('Your Channel Access Token ')  # Channel Access Token
handler = WebhookHandler('Your Channel Secret ')  # Channel Secret

# 設置 OpenAI API 密碼
openai.api_key = "Your OpenAI API Key"  # OpenAI API Key

# 初始化 Redis 客户端
redis_client = redis.StrictRedis(host='example.com', port=00000, db=0, username='default', password='Your Password',protocol=0 ,decode_responses=True)

#機器人基本資料
dafault_memory = {
    "role": "system", 
    "content": "Your Bot setting"
}

# 暫時存取用户名稱
def get_user_name(user_id):
    cache_key = f"user_name:{user_id}"
    
    # 檢查 Redis 暫存
    user_name = redis_client.get(cache_key)
    if user_name:
        return user_name  # 從暫存中返回
    
    # 如果暫存中没有，則調用 LINE API 獲取
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    
    # 將用户名稱暫存到 Redis，有效期設為 1 天
    redis_client.setex(cache_key, 24*60*60 , user_name)
    return user_name

#前天
def get_before_yesterday_key(type):
    now = datetime.now()
    before_yesterday = now - timedelta(days=2)
    yyyymmdd = before_yesterday.strftime("%Y-%m-%d")
    return 'history-' + type + '-' + yyyymmdd

#昨天
def get_yesterday_key(type):
    now = datetime.now() 
    yesterday = now - timedelta(days=1)
    yyyymmdd = yesterday.strftime("%Y-%m-%d")
    return 'history-' + type + '-' + yyyymmdd

# 當前日期和時間
def get_today_key(type): 
    now = datetime.now()
    yyyymmdd = now.strftime("%Y-%m-%d")
    return 'history-' + type + '-' + yyyymmdd

redis_client.delete(get_before_yesterday_key('chat'), get_before_yesterday_key('talk'))  # 清除chat舊歷史 & talk舊歷史

print("<delete chat> history size:", redis_client.llen(get_before_yesterday_key('chat')))
print("<delete talk> history size:", redis_client.llen(get_before_yesterday_key('talk')))
    
# 初始化對話歷史
def init_today(type): 
    today_key = get_today_key(type)

    # 如果 Redis 中不存在該歷史紀錄，初始化為機器人基本資料
    if not redis_client.exists(today_key):
        redis_client.rpush(today_key, json.dumps(dafault_memory))  # 寫入機器人初始資料
        
    print("<init_today> today_key:", today_key)
    print("<iinit_today> history size:", redis_client.llen(today_key))
    return today_key

# 定義獲取回答的函数
def get_answer(yesterday_key, today_key, user_name, user_message):
    # 從 Redis 獲取歷史紀錄
    redis_yesterday_history = redis_client.lrange(yesterday_key, 0, -1)
    yesterday_data = [eval(item) for item in redis_yesterday_history if item]
    
    redis_today_history = redis_client.lrange(today_key, 0, -1)
    today_data = [eval(item) for item in redis_today_history if item]  # 轉換回字典列表
    
    
    # 避免重複添加相同的用户訊息
    if not today_data or today_data[-1].get("content") != user_message:
        today_data.append({"role": "user", "content": user_name + " 說: " + user_message})
    
    total_data = []
    
    for item in yesterday_data:
       total_data.append(item)
    
    for item in today_data:
       total_data.append(item)
       
    print("total_data <= ", total_data)


    # 将新的用户消息添加到 Redis
    redis_client.rpush(today_key, str({"role": "user", "content": user_message}))

    try:
        print("<get_answer> openai send message =>", total_data)
        response = openai.ChatCompletion.create(
            model = "gpt-4o",
            messages = total_data,
            temperature = 0.5,
            max_tokens = 2048
        )
        answer = response.choices[0].message['content'].strip()
        print("<get_answer> openai reply answer <=", answer)

        # 確保助理的回應也不会重复
        if not today_data or today_data[-1].get("content") != answer:
            today_data.append({"role": "assistant", "content": answer})

            # 將助理的回應添加到 Redis
            redis_client.rpush(today_key, str({"role": "assistant", "content": answer}))

        print("<get_answer> history size:", redis_client.llen(today_key))
        return answer
    except Exception as e:
        return f"抱歉，處理您的請求時發生錯誤: {str(e)}"

# Webhook 路徑，用来接收 Line 消息
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
    return 'OK'

# 處理 Line 傳来的消息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    if user_message.startswith('/'):
        command = user_message.split(" ", 1)[0]
        parameters = user_message[len(command) + 1:]  # 加1用以略過空格
        print("@command:", command)
        print("@parameters:", parameters)

        if command == '/sum' or command == '/s':
            today_key = get_today_key('chat')
            yesterday_key = get_yesterday_key('chat')
            
            all_chat = ""
            #從redis抓昨天資料
            for element in redis_client.lrange(yesterday_key, 0, -1):
                if element:
                    element_dict = eval(element)
                    if element_dict.get("role") == "user":
                        all_chat += element_dict.get("content") + "\n"
                    
            #從redis抓今天資料
            for element in redis_client.lrange(today_key, 0, -1):
                if element:
                    element_dict = eval(element)
                    if element_dict.get("role") == "user":
                        all_chat += element_dict.get("content") + "\n"
                        
            print("<sum> all_chat:", all_chat)
            sum_data = [{"role": "user", "content": f"用繁體中文「條列式精簡」總結聊天室的內容，內容為: {all_chat}"}]
        
            print("<sum> sum_data:", sum_data)
            
            response = openai.ChatCompletion.create(
                model = "gpt-4o",  
                messages = sum_data,
                max_tokens = 2048,
                temperature = 0.5,
            )
            result = response.choices[0].message['content'].strip()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))

        elif command == '/talk' or command == '/t':
            user_id = event.source.user_id  # 獲取用户 ID
            user_name = get_user_name(user_id)  # 獲取用户的暱稱
            
            today_key = init_today('talk')
            yesterday_key = get_yesterday_key('talk')
            
            answer = get_answer(yesterday_key, today_key, user_name, parameters)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answer))
        
        elif command == '/help' or command == '/?':
            help_message = (
                "可用的指令：\n"
                "/sum <内容> - 總結聊天室訊息\n"
                "/talk <内容> - 和ChatGPT對話並保留對話紀錄\n"
                "/help - 顯示幫助訊息\n"
                "小技巧: 可以簡化指令為/s、/t、/?"
            )
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_message))
            return  # 不做任何事
        
        else:  # 錯誤訊息
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請输入有效的指令，如 /sum 、/talk、/help或/?"))
            return  # 不做任何事
        
    else:
        today_key = init_today('chat')
        print("<chat> today_key:", today_key)
        redis_history = redis_client.lrange(today_key, 0, -1)
        history = [eval(item) for item in redis_history if item]  # 轉換回字典列表
        if not history or history[-1].get("content") != user_message:
           # 避免重複添加相同的用户訊息
           redis_client.rpush(today_key, str({"role": "user", "content": user_message}))

# ===============================================================

# 定義 /history 路徑的功能
@app.route("/history")
def history():
    # 指定要讀取的 Redis key
    keys = [get_yesterday_key('chat'), get_today_key('chat')]
    data = []

    # 從 Redis 中讀取每個 key 的列表
    for key in keys:
        print("key <= ", key)
        redis_history = redis_client.lrange(key, 0, -1)  # 讀取該 key 下所有元素
        
        history = [eval(item) for item in redis_history if item]  # 转换回字典列表
        
        # data.append(history)
        for item in history:
            data.append(item)
    
    # HTML 模板，生成表格來顯示資料
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Chat History</title>
        <style>
            table {
                width: 50%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid black;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <h2>Chat History</h2>
        <table>
            <thead>
                <tr>
                    <th>Role</th>
                    <th>Content</th>
                </tr>
            </thead>
            <tbody>
                {% for item in data %}
                <tr>
                    <td>{{ item.role }}</td>
                    <td>{{ item.content }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """

    # 生成 HTML，並將資料傳遞到模板中
    return render_template_string(html_template, data=data)

# ===============================================================

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)