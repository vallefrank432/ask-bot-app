from flask import Flask, request, render_template, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import csv
import random
import time

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp'
RESULT_FILE = '/tmp/ad_results.csv'

def get_random_proxy(proxies):
    return random.choice(proxies)

def random_delay(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def run_bot(proxies_file, keywords_file):
    # Read proxies and keywords
    with open(proxies_file, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    with open(keywords_file, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]

    with open(RESULT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Keyword', 'Ad Text', 'Ad URL'])

        for keyword in keywords:
            proxy = get_random_proxy(proxies)
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f'--proxy-server={proxy}')

            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://www.ask.com/")
            random_delay()

            search_box = driver.find_element(By.NAME, "q")
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            random_delay(3, 6)

            ads = driver.find_elements(By.CSS_SELECTOR, ".ads a")
            for ad in ads:
                text = ad.text.strip()
                url = ad.get_attribute("href")
                writer.writerow([keyword, text, url])

            driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        proxies_file = os.path.join(UPLOAD_FOLDER, 'proxies.txt')
        keywords_file = os.path.join(UPLOAD_FOLDER, 'keywords.txt')

        request.files['proxies'].save(proxies_file)
        request.files['keywords'].save(keywords_file)

        run_bot(proxies_file, keywords_file)
        return render_template('index.html', status="Bot finished! Download your results below.")
    return render_template('index.html', status="")

@app.route('/download')
def download():
    return send_file(RESULT_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
