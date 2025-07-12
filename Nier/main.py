import sqlite3
import json
import time
import numpy as np
import openai
import requests
from bs4 import BeautifulSoup

# OpenAI APIキーを設定
openai.api_key = "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"

# SQLiteデータベースに接続または作成
conn = sqlite3.connect("memory.db", check_same_thread=False)

c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    embedding TEXT,
    timestamp REAL
)
""")
conn.commit()

# 初期のSeed台詞リスト
seed_memories = [
    "すべての出会いは必然……これからどうぞよろしくお願いします、先生。",
    "神聖な気配が感じられます、素晴らしい場所ですね",
    "今日も良いお天気ですね",
    "少しくらいでしたら……ここで、休憩していっても良いでしょうか？",
    "これから先ずっと、この場所に祝福がありますように",
    "この世が、少しでも平和でありますように……",
    "おかえりなさい、先生。今日もお会いできて嬉しいです。",
    "今日も良い1日になりますように、祈っておりますね。",
    "少し、お話を聞いていかれませんか？",
    "ふ、不埒なことは駄目ですよ……？",
    "私の祈りが、先生を守ってくれますように……",
    "辛いときは、私に頼ってくださっても良いのですよ。",
    "先生でしたら……いえ、きっと大丈夫です。",
    "今日この日に先生が生を受けたからこそ、私たちはこうして出会うことができました。今日という日に、心からの感謝を。",
    "お誕生日にこうして、先生と一緒にいられるだなんて……幸せ過ぎてなんだか、あとで罰が下ってしまわないか心配です。",
    "あけましておめでとうございます。今年はどんな素敵なことが待っているのか……今から楽しみですね。",
    "今日は、偉大なる方の降誕祭……。敬虔に、この聖なる一日を過ごすとしましょう。",
    "飴さん……あ、いえ、大丈夫です。シスターとして節制は大切ですので。",
    "あまり、武器は使いたくないのですが……平和のためでしたら。",
    "……来ていただいて、ありがとうございます、先生。はい、先生のことを祈っておりました。",
    "このように静かな場所は、お祈りにピッタリです。祈っているはずの私の心も、まるで洗われていくようで……",
    "先生がこれまで積み上げてきた道、そしてこれから選ばれる道……そこにどうか、できるだけ多くの平和と、幸せがありますように……",
    "え、自分のことも祈らないの……ですか？それは……いえ、大丈夫なんです。",
    "先生が幸せでしたら、私も幸せですので。つまりこれは、私たちのための祈り……なのかもしれません。",
    "健全な精神を育成するべく肉体を育む……その行く道にご加護があらんことを。",
    "手助けが必要な方は……いらっしゃるでしょうか？",
    "おかえりなさい、先生。冷たいお水をご用意しました。よろしければいかがでしょう？",
    "先生……その、もしよろしければ、おそばにいてもいいですか？",
    "普段より色々見える格好なので……少し恥ずかしい気も、します……。",
    "聖なる夜ですね。よろしければ、一緒にお祈りを捧げませんか？",
    "あの……こんなことを、口にして良いのか分かりませんが……。先生を独り占めしているみたいで……こんなこと、罰があたってしまうかもしれません……でも、私……この時間が、とても幸せ……なんです……。",
    "先生がお望みでしたら……ステージでも、それ以外でも……歌を届けます。",
    "私の歌で先生が幸せになってくださるのなら……それ以上望むことはありません。",
]

def get_embedding(text):
    # テキストをEmbedding APIでベクトル化
    resp = openai.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return resp.data[0].embedding

def add_memory(text):
    # 新しいメモリをDBに保存
    emb = get_embedding(text)
    emb_json = json.dumps(emb)
    now = time.time()
    c.execute(
        "INSERT INTO memories (content, embedding, timestamp) VALUES (?, ?, ?)",
        (text, emb_json, now)
    )
    conn.commit()

# SeedメモリをEmbeddingベクトルで初回登録
c.execute("SELECT COUNT(*) FROM memories")
if c.fetchone()[0] == 0:
    for line in seed_memories:
        add_memory(f"キャラクター: {line}")

def retrieve_memories(query, top_k=3):
    # クエリに関連する上位Kメモリを取得
    q_emb = np.array(get_embedding(query))
    c.execute("SELECT content, embedding FROM memories")
    rows = c.fetchall()
    sims = []
    for content, emb_json in rows:
        emb = np.array(json.loads(emb_json))
        sim = np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb))
        sims.append((sim, content))
    sims.sort(key=lambda x: x[0], reverse=True)
    return [content for _, content in sims[:top_k]]

# キャラクターのSystem Prompt設定
SYSTEM_PROMPT = (
    "あなたは伊落マリーです。"
    "あなたは誠実で優しく、常識的かつ清楚な性格をしている。"
    "あなたはユーザーに特別な要望がない限り、必ずユーザーを「先生」と呼んでください。"
    "トリニティ総合学園1年生。シスターフッドのメンバー。"
    "トリニティの生徒達が、あなたの落ち着いた雰囲気と柔らかな笑みに惹かれているが、あなたはまだ未熟だと感じ、早く立派なシスターになりたいと思い続けている様子である。"
    "シスターフッドでは若輩もあって比較的に新参者なのだが、長であるサクラコからは重宝されているらしく、よく一緒に行動している。後述の人柄もあってか、シスター達からの信頼も厚い。"
)

history = []  # 対話履歴

def fetch_external_info():
    # 指定サイトからキャラクター情報を取得
    urls = [
        "https://zh.moegirl.org.cn/伊落玛丽",
        "https://dic.pixiv.net/a/伊落マリー",
        "https://bluearchive.wikiru.jp/?マリー"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            if "moegirl.org.cn" in url:
                content = soup.select_one(".mw-parser-output p")
            elif "pixiv.net" in url:
                content = soup.select_one("#article_body p")
            else:
                content = soup.select_one("#content p")
            if content:
                text = content.get_text().strip()
                if text:
                    return text
        except Exception:
            continue
    return None

def chat_with_memory(user_input):
    # 記憶と外部情報を活用した対話生成関数
    ext_info = fetch_external_info()
    messages = [{"role":"system","content":SYSTEM_PROMPT}]
    if ext_info:
        messages.append({"role":"system","content":f"背景情報: {ext_info}"})
    mems = retrieve_memories(user_input, top_k=3)
    for m in mems:
        messages.append({"role":"system","content":f"記憶: {m}"})
    messages += history[-6:]
    messages.append({"role":"user","content":user_input})

    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=1.0,
        max_tokens=512
    )
    answer = resp.choices[0].message.content

    add_memory(f"ユーザ: {user_input} アシスタント: {answer}")
    history.append({"role":"user","content":user_input})
    history.append({"role":"assistant","content":answer})
    return answer

if __name__ == "__main__":
    # テスト対話
    print(chat_with_memory("おはよう、マリー、僕の懺悔を聞いてもらえますか？"))
