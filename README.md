# 百人一首クイズアプリ

百人一首の和歌を使ったクイズアプリです。  
Streamlitで作成しています。

## 特徴
- 百人一首の「下の句当て」「作者当て」モード
- 解説・作者情報表示
- スコア管理
- モバイル対応デザイン

## 必要ファイル
- `hyakunin_isshu_game/app.py`（メインアプリ）
- `hyakunin_isshu_game/hyakunin_isshu.json`（百人一首データ）
- `requirements.txt`（依存パッケージ）

## ローカル実行方法

```bash
pip install -r requirements.txt
streamlit run hyakunin_isshu_game/app.py
```

## Streamlit Cloudへのデプロイ方法

1. 本リポジトリをGitHubにpush
2. Streamlit Cloud（https://streamlit.io/cloud）にアクセスし、GitHub連携
3. 「New app」からリポジトリ・ブランチ・`hyakunin_isshu_game/app.py`を指定してデプロイ

