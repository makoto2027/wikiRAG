from langchain_chroma import Chroma
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from selenium import webdriver
import csv
from tqdm import tqdm
import json

from functions import get_text, chunk_text, convertDocuments

with open("code/RAG/config.json", "r") as f:
    config = json.load(f)


storePath = "code/RAG/chroma_data_300"
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=config["OPENAI_API_BASE"],
    openai_api_key=config["OPENAI_API_KEY"],
    deployment='text-embedding-ada-002', # 使うモデル
    chunk_size=300
)

vectorstore = Chroma(
    collection_name="my_collection",
    persist_directory=storePath,
    embedding_function=embeddings
)

f = open('code/RAG/text/urls.txt', 'r')
urls = [url.strip() for url in f.readlines()]
f.close()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(300)

notGetUrl = []
saveFilePath = "code/RAG/text/failedUrl.txt"


# 進捗バーの初期化
with tqdm(total=len(urls), desc="Processing URLs", unit="url") as pbar:
    for url in urls:
        try:
            # ページからテキストを取得
            page_text = get_text(url, driver)

            if not page_text:
                pbar.write(f"Warning: No content found for {url}")  # 必要に応じて進捗バーに警告を表示
                pbar.update(1)
                print(f"Skipping URL (no content found): {url}")
                notGetUrl.append(url)
                continue

            # チャンキング
            chunks = chunk_text(page_text, 300, 30)

            # Document オブジェクト化
            documents = convertDocuments(chunks, url)

            # データベースに保存
            vectorstore.add_documents(documents)

        except Exception as e:
            pbar.write(f"Error processing {url}: {e}")  # 必要に応じてエラーメッセージを表示

        # 進捗バーを更新
        pbar.update(1)

driver.quit()


with open(saveFilePath, 'w') as f:
    writer = csv.writer(f, delimiter="\n")
    writer.writerow(notGetUrl)