from flask import Flask, render_template, request, send_file
from pptx import Presentation
import io
import os
from groq import Groq

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
    content = request.form.get("content")

    prompt = f"""
다음 조사 내용을 PPT 슬라이드 구조로 요약해줘.

조건
- 5~7 슬라이드
- 각 슬라이드는 제목 + 핵심 3줄

내용:
{content}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}]
    )

    result = response.choices[0].message.content

    return render_template(
        "preview.html",
        title=title,
        name=name,
        result=result,
        content=content
    )


@app.route("/generate", methods=["POST"])
def generate():

    title = request.form.get("title")
    name = request.form.get("name")
    result = request.form.get("result")

    slides = result.split("\n\n")

    prs = Presentation()

    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)

    slide.shapes.title.text = title
    slide.placeholders[1].text = name

    for s in slides:

        if not s.strip():
            continue

        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)

        parts = s.split("\n")

        slide.shapes.title.text = parts[0]

        slide.placeholders[1].text = "\n".join(parts[1:])

    file_stream = io.BytesIO()
    prs.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="slidr_presentation.pptx",
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@app.route("/feedback", methods=["POST"])
def feedback():

    message = request.form.get("message")

    with open("feedback.txt","a",encoding="utf-8") as f:
        f.write(message+"\n")

    return "ok"


if __name__ == "__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
