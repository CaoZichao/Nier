import os
import threading
from flask import Flask, request, jsonify, send_file
from main import chat_with_memory

# Flaskアプリ初期化
app = Flask(__name__)

# HTMLテンプレート（1ファイルで完結）
HTML = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>Nier Chat</title>
  <style>
    body { display: flex; margin: 0; height: 100vh; font-family: sans-serif; }
    #avatar { flex: 0 0 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; }
    #avatar img { width: 150px; border-radius: 50%; }
    #chat { flex: 1; display: flex; flex-direction: column; }
    #messages { flex: 1; display: flex; flex-direction: column; padding: 10px; overflow-y: auto; background: #fafafa; }
    .message { display: inline-block; padding: 8px 12px; border-radius: 16px; margin: 5px; max-width: 60%; font-size: 18px; color: #000; }
    .message.user { background: #dcf8c6; align-self: flex-end; }
    .message.bot  { background: #e5e5ea; align-self: flex-start; }
    #input { display: flex; padding: 10px; border-top: 1px solid #ccc; }
    #input input { flex: 1; padding: 8px; font-size: 18px; }
    #input button { padding: 8px 16px; font-size: 18px; margin-left: 5px; }
  </style>
</head>
<body>
  <div id="avatar">
    <img src="/avatar" alt="Avatar">
  </div>
  <div id="chat">
    <div id="messages"></div>
    <div id="input">
      <input id="user-input" type="text" placeholder="先生: メッセージを入力">
      <button id="send-btn">送信</button>
    </div>
  </div>
  <script>
    const messagesDiv = document.getElementById('messages');
    const inputBox = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    function addMessage(text, cls) {
      const div = document.createElement('div');
      div.className = 'message ' + cls;
      div.textContent = text;
      messagesDiv.appendChild(div);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    sendBtn.onclick = async function() {
      const text = inputBox.value.trim();
      if (!text) return;
      addMessage('先生: ' + text, 'user');
      inputBox.value = '';
      const resp = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await resp.json();
      addMessage('マリー: ' + data.reply, 'bot');
    };
    inputBox.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') sendBtn.click();
    });
  </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    reply = chat_with_memory(user_input)
    return jsonify({'reply': reply})

@app.route('/avatar')
def avatar():
    # プロジェクトルートに置いた Avatar.jpg を返す
    return send_file('Avatar.jpg', mimetype='image/jpeg')

if __name__ == '__main__':
    # サーバ起動
    app.run(port=5000)
