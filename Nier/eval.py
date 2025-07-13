#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用方法：
1. 安装依赖：
   pip install --upgrade openai numpy tqdm argparse
2. 设置环境变量（或直接在脚本中填写 API Key）：
   export OPENAI_API_KEY="你的真实API Key"
3. 运行评估：
   python eval.py /Users/lime/Desktop/Nier/baseline.jsonl /Users/lime/Desktop/Nier/rag.jsonl
"""

import os
import json
import argparse
import numpy as np
from tqdm import tqdm

# 必要ライブラリをインポート
import openai

# 1. OpenAI APIキーの設定（環境変数または直接記述）
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

# 2. Embedding取得関数
def get_embedding(text):
    # テキストをEmbeddingモデルに送信してベクトルを取得
    res = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    # 新APIでは res.data[0].embedding にアクセス
    return np.array(res.data[0].embedding)

# 3. コサイン類似度計算
def cosine_sim(a, b):
    # 余弦類似度を計算（ゼロ除算防止に小さな値を足す）
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)

# 4. 平均関連度の計算
def avg_relevance(samples):
    sims = []
    for s in tqdm(samples, desc="関連度計算"):
        emb_u = get_embedding(s["user"])
        emb_r = get_embedding(s["reply"])
        sims.append(cosine_sim(emb_u, emb_r))
    return float(np.mean(sims)) if sims else 0.0

# 5. Distinct-2 の計算
def distinct_n(texts, n=2):
    total = 0
    uniq = set()
    for t in texts:
        tokens = t.split()
        for i in range(len(tokens) - n + 1):
            uniq.add(tuple(tokens[i:i+n]))
            total += 1
    return float(len(uniq) / total) if total > 0 else 0.0

# 6. システム評価
def eval_system(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")
    samples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            samples.append(json.loads(line))
    rel = avg_relevance(samples)
    distinct2 = distinct_n([s["reply"] for s in samples], 2)
    score = (rel + distinct2) / 2
    return rel, distinct2, score

def main():
    parser = argparse.ArgumentParser(description="Baseline と RAG-System の評価")
    parser.add_argument("baseline_path", help="baseline.jsonl のパス")
    parser.add_argument("rag_path", help="rag.jsonl のパス")
    args = parser.parse_args()

    # Baseline 系统评估
    baseline_rel, baseline_d2, baseline_score = eval_system(args.baseline_path)
    # RAG-System 系统评估
    rag_rel, rag_d2, rag_score = eval_system(args.rag_path)

    # 输出对比结果
    print("=== 结果比较 ===")
    print(f"Baseline:    Rel={baseline_rel:.4f}, Distinct-2={baseline_d2:.4f}, Score={baseline_score:.4f}")
    print(f"RAG-System:  Rel={rag_rel:.4f}, Distinct-2={rag_d2:.4f}, Score={rag_score:.4f}")

if __name__ == "__main__":
    main()
