from functions import get_urls
import csv

BaseUrl = "https://wikiwiki.jp/syanhuro/" # Wikiのホームページ
saveFilePath = "code/RAG/urls.txt"

urls = [BaseUrl]

urls1st = get_urls(urls)

urls2nd = get_urls(urls1st)

filtered_urls = [url for url in urls2nd if "//wikiwiki.jp/syanhuro/?cmd=" not in url]

filtered_urls.sort()

with open(saveFilePath, 'w') as f:
    writer = csv.writer(f, delimiter="\n")
    writer.writerow(filtered_urls)