# 社会福祉士国家試験 法令検索AI (Rust + Python Hybrid)

高速な検索と、法令の全文閲覧が可能なAI検索システムです。
バックエンドにRustを採用し、ベクトル検索の高速化とメモリ効率の最適化を行っています。

## 特徴
1. **AI検索**: Google Geminiを活用した「検索意図（Intent）」の理解と、高精度なベクトル検索。
2. **高速レスポンス**: Rust (`Axum`) による爆速バックエンドサーバー。
3. **法令閲覧**: 全文閲覧モードと、条文へのジャンプ機能付き目次。

## 必要要件
- OS: Windows (推奨), Mac, Linux
- **Python**: 3.10 以上 [ダウンロード](https://www.python.org/downloads/)
- **Rust**: 最新版 [ダウンロード](https://www.rust-lang.org/tools/install)
- **Google API Key**: Gemini APIを利用するために必要 [取得はこちら](https://aistudio.google.com/app/apikey)

## インストールと起動方法

### 1. リポジトリの準備
```bash
git clone <REPOSITORY_URL>
cd law-scraping-system
```

### 2. APIキーの設定
プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下のようにAPIキーを記述してください。

**ファイル名:** `.env`
```env
GOOGLE_API_KEY=your_actual_api_key_here
```
※ 起動時にバックエンド側へ自動的にコピーされます。

### 3. 初期セットアップ（初回のみ）
必要なPythonライブラリをインストールします。

```bash
pip install -r requirements.txt
```

### 4. アプリケーションの起動
以下のコマンドを実行すると、Rustバックエンドのコンパイル・実行と、フロントエンドの起動が一括で行われます。

```bash
python start_app.py
```

* 初回起動時はRustのコンパイルに数分かかる場合があります。
* 起動後、ブラウザで `http://localhost:8501` が自動的に開きます。

## トラブルシューティング

- **Rustのエラー**: `cargo` コマンドが見つからない場合は、Rustをインストールしてください。
- **APIキーエラー**: `.env` ファイルが正しい場所（ルート）にあるか確認してください。
