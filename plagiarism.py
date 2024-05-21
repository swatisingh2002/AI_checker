from flask import Flask, request, render_template, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import requests
import json

app = Flask(__name__)

def read_file(file):
    return file.read().decode('utf-8')

def vectorize(texts):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    return tfidf_matrix.toarray()

def similarity(doc1, doc2):
    return cosine_similarity([doc1], [doc2])[0][0]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    result = None
    if request.method == 'POST':
        if 'file1' not in request.files or 'file2' not in request.files:
            return "Please upload both files", 400

        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1.filename == '' or file2.filename == '':
            return "Please select both files", 400

        text1 = read_file(file1)
        text2 = read_file(file2)
        student_notes = [text1, text2]

        vectors = vectorize(student_notes)
        sim_score = similarity(vectors[0], vectors[1])
        sim_score = round(sim_score, 2)

        student_a = os.path.splitext(file1.filename)[0]
        student_b = os.path.splitext(file2.filename)[0]
        result = f"{student_a} is {sim_score * 100}% similar to {student_b}"

    return render_template('upload.html', result=result)

@app.route('/check', methods=['GET', 'POST'])
def check_text():
    result = None
    if request.method == 'POST':
        text_to_check = request.form['text_to_check']

        burp0_url = "https://papersowl.com:443/plagiarism-checker-send-data"
        burp0_cookies = {
            "PHPSESSID": "qjc72e3vvacbtn4jd1af1k5qn1",
            # (other cookies here)
        }

        burp0_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://papersowl.com/free-plagiarism-checker",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://papersowl.com",
            "Dnt": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Te": "trailers",
            "Connection": "close"
        }

        burp0_data = {
            "is_free": "false",
            "plagchecker_locale": "en",
            "product_paper_type": "1",
            "title": '',
            "text": str(text_to_check)
        }

        try:
            r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)
            r.raise_for_status()
            result = r.json()

            matches = [{"url": match["url"], "percent": match["percent"]} for match in result.get("matches", [])]

            response_data = {
                "word_count": result.get("words_count", "N/A"),
                "Plagiarism": 100 - float(result.get("percent", 0)),
                "matches": matches
            }
        except requests.exceptions.RequestException as e:
            result = {"error": str(e)}
        except json.JSONDecodeError as e:
            result = {"error": "Failed to parse JSON response: " + str(e)}

    return render_template('check.html', result=result)

if __name__ == "__main__":
    app.run(debug=True, port=5555)
# http://127.0.0.1:5555/