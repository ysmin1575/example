from flask import Flask, render_template, request, send_file, redirect, url_for
from pptx import Presentation
import io
import os

# Groq 선택적 로딩 (API 키 없어도 서버 실행됨)
try:
    from groq import Groq
    groq_key = os.environ.get("GROQ_API_KEY")

    if groq_key:
        client = Groq(api_key=groq_key)
    else:
        client = None
except:
    client = None


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generator")
def generator():
    return render_template("generator.html")


@app.route("/preview", methods=["POST"])
def preview():

    title = request.form.get("title")
    name = request.form.get("name")
    content = request.form.get("content", "")
    
    # AI 사용 가능
    if client:

        prompt = f"""
다음 내용을 PPT 슬라이드로 정리해줘.

조건
- 5~7 슬라이드
- 각 슬라이드는 한 문장 요약

내용:
{content}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}]
        )

        result = response.choices[0].message.content.split("\n")

    else:
        # AI 없으면 기본 분리
        result = content.split("\n")

    slides = [s for s in result if s.strip()]

    return render_template(
        "preview.html",
        title=title,
        name=name,
        slides=slides
    )


@app.route("/generate", methods=["POST"])
def generate():

    title = request.form.get("title")
    name = request.form.get("name")
    slides = request.form.getlist("slides")

    prs = Presentation()

    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)

    slide.shapes.title.text = title
    slide.placeholders[1].text = name

    for s in slides:

        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)

        slide.shapes.title.text = "내용"
        slide.placeholders[1].text = s

    file_stream = io.BytesIO()
    prs.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="slidr_ppt.pptx",
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@app.route("/feedback", methods=["POST"])
def feedback():

    message = request.form.get("message")

    if message:
        with open("feedback.txt","a",encoding="utf-8") as f:
            f.write(message+"\n")

    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
