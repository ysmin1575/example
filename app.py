from flask import Flask, render_template, request, send_file
from pptx import Presentation
import io
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generator")
def generator():
    return render_template("generator.html")

@app.route("/generate", methods=["POST"])
def generate():

    title = request.form.get("title")
    name = request.form.get("name")
    content = request.form.get("content")

    paragraphs = content.split("\n")

    prs = Presentation()

    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)

    slide.shapes.title.text = title
    slide.placeholders[1].text = name

    for p in paragraphs:

        if not p.strip():
            continue

        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)

        slide.shapes.title.text = "내용"
        slide.placeholders[1].text = p

    file_stream = io.BytesIO()
    prs.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="presentation.pptx",
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

@app.route("/feedback", methods=["POST"])
def feedback():

    message = request.form.get("message")

    with open("feedback.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
