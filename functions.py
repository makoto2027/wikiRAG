from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException
from urllib.parse import urlparse
from langchain.schema import Document
from datetime import datetime
import hashlib
from langchain_chroma import Chroma
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
import json

with open("scripts/config.json", "r") as f:
    config = json.load(f)


def get_urls (urls:list):
    driver = webdriver.Chrome() # webdriverはChromeを使う
    driver.set_page_load_timeout(300)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")

    for page in range(len(urls)):
        driver.get(urls[page]) # ページを開く

        for _ in range(5):  # 最大5回までリトライ
            try:
                # 最新のリンク要素を取得
                links = driver.find_elements(By.TAG_NAME, "a")

                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        parsed_url = urlparse(href)
                        
                        # フラグメント部分が存在するか、もしくは無効なリンクを除外
                        if parsed_url.fragment:  # フラグメント（#以降）が存在する場合
                            continue

                        # wikiwiki.jp/syanhuro/ のみ取得
                        if "wikiwiki.jp/syanhuro/" in href and href not in urls:
                            urls.append(href)

                break  # 正常に完了した場合はループを抜ける
            except StaleElementReferenceException:
                # 要素が無効化された場合、再試行
                print("StaleElementReferenceException: Retrying...")

    driver.quit()
    urls.sort()

    return urls


def get_text (url:str, driver):
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content_element = soup.find(id="content")

    if content_element:
        return content_element.get_text(separator=" ", strip=True)
    else:
        return ""


def chunk_text(text:str, chunk_size:int, overlap:int):
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


def convertDocuments(chunks:list, metadata:str):
    documents = []
    doc_date = datetime.now().strftime("%Y-%m-%d")

    for chunk in chunks:
        unique_string = chunk + metadata  # 必要に応じて追加するメタデータを拡張可能
        doc_id = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()
        
        document = Document(
            page_content=chunk,
            metadata={"source": metadata, "date": doc_date, "id": doc_id}  # メタデータに ID を追加
        )
        documents.append(document)

    return documents


def searchChunk(path:str, input:str, N:int):
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=config["OPENAI_API_BASE"],
        openai_api_key=config["OPENAI_API_KEY"],
        deployment='text-embedding-ada-002', # 使うモデル
        chunk_size=500
    )

    vectorstore = Chroma(
        collection_name="my_collection",
        persist_directory=path,
        embedding_function=embeddings
    )

    docs = vectorstore.similarity_search(input, k=N)

    texts = [doc.page_content for doc in docs]
    urls = urls = [doc.metadata.get("source", "URLなし") for doc in docs]

    urls_set = set(urls)
    urls_list = list(urls_set)

    return texts, urls_list


def Answer_question(question:str, serch_result:list):
    error_flg = False
    llm = AzureChatOpenAI(
        openai_api_version=config["OPENAI_API_VERSION"],
        azure_endpoint=config["OPENAI_API_BASE"],
        openai_api_key=config["OPENAI_API_KEY"],
        azure_deployment=config["OPENAI_API_ENGINE"],
        temperature=0
    )

    template = '''
    【検索結果】を基に【質問】に答えてください。
    回答のみを出力してください。

    【質問】
    {input1}

    【検索結果】
    {input2}
    '''

    prompt_template = PromptTemplate(
        input_variables=['input1', 'input2'],
        template=template
    )

    text = '¥n¥n'.join([doc for doc in serch_result])

    try:
        chain = prompt_template | llm
        ans = chain.invoke({"input1": question, "input2": text})
        return ans.content if hasattr(ans, 'content') else str(ans), error_flg
    except Exception as e:
        error_flg = True
        error_message = str(e)

        if "context_length_exceeded" in error_message:
            return "トークン数が制限を超えました。チャンク数を減らしてください。", error_flg
        return f"エラーが発生しました: {error_message}", error_flg