# README

## 1. 仮想環境の構築（venv）

> ※ Python のバージョンを固定したい場合は、**pyenv** などで先に目的の Python を入れておき、その Python で下記コマンドを実行してください。  
> 例: `pyenv local 3.12.6` の後に `python -m venv .venv`

### 1-1. 仮想環境の作成
```bash
python -m venv .venv
```

### 1-2. 仮想環境の起動／終了

**macOS / Linux（bash/zsh）**
```bash
# 起動
source .venv/bin/activate

# 終了
deactivate
```

**Windows（PowerShell）**
```powershell
# 起動
.\.venv\Scripts\Activate.ps1

# 終了
deactivate
```
> PowerShell の実行ポリシーで起動できない場合（権限が許される範囲で一時的に回避）  
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

**Windows（コマンドプロンプト/CMD）**
```cmd
:: 起動
.\.venv\Scriptsctivate.bat

:: 終了
deactivate
```

### 1-3. 依存パッケージのインストール
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. データベースの作成

### 2-1. URL 収集（例）
```bash
python scripts/getURLs.py
# 例: 引数がある場合
# python scripts/getURLs.py --keyword "example" --out data/urls.json
```

### 2-2. DB 作成
```bash
python scripts/createDB.py
# 例: 引数がある場合
# python scripts/createDB.py --in data/urls.json --db data/app.db
```

> メモ
> - `data/` フォルダが必要なら作成しておく：`mkdir -p data`（Windowsは `mkdir data`）
> - `.env` を読む実装の場合は `cp .env.example .env`（Windowsは `copy .env.example .env`）して値を設定
> - パス解決エラーが出る場合はリポジトリルートで `export PYTHONPATH=.`（Windows PowerShell は `$env:PYTHONPATH='.'`）を試してください

---

## 3. アプリの起動（Streamlit）

```bash
# リポジトリのルートで実行
streamlit run scripts/main.py
```
