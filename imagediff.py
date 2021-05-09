from flask import Flask, render_template, request, redirect
from PIL import Image, ImageColor
from flask.helpers import flash
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)
app.config["SECRET_KEY"] = "353ed1fcc88a4f1cdfddee751f0cf877"


def save_img_to_str(img: Image) -> str:
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "image1" not in request.files or "image2" not in request.files:
            flash("Image(s) not found!")
            return redirect(request.url)
        if "highlight-color" not in request.form:
            flash("Highlight color not found!")
            return redirect(request.url)

        image1 = request.files["image1"]
        image2 = request.files["image2"]

        if image1.filename == "" or image2.filename == "":
            flash("No filename found on image(s)!")
            return redirect(request.url)

        image1 = Image.open(image1).convert("RGB")
        image2 = Image.open(image2).convert("RGB")

        if image1.width != image2.width or image1.height != image2.height:
            flash(
                f"Images are not of same width! (Image1 size: ({image1.width}, {image1.height}), Image2 size: ({image2.width}, {image2.height})"
            )
            return redirect(request.url)

        output = Image.new("RGBA", (image1.width, image1.height))

        image1_arr = np.asarray(image1)
        image2_arr = np.asarray(image2)
        image_black_and_white_arr = np.asarray(image1.convert("L").convert("RGB"))

        for y, (row1, row2, row3) in enumerate(zip(image1_arr, image2_arr, image_black_and_white_arr)):
            for x, (color1, color2, color3) in enumerate(zip(row1, row2, row3)):
                if np.array_equal(color1, color2):
                    output.putpixel((x, y), tuple([color3[0], color3[1], color3[2], 100]))
                else:
                    output.putpixel(
                        (x, y), ImageColor.getrgb(request.form["highlight-color"])
                    )

        context = {
            "diff": True,
            "image1_data": save_img_to_str(image1),
            "image2_data": save_img_to_str(image2),
            "diff_data": save_img_to_str(output),
            "highlight_color": request.form["highlight-color"]
        }
        return render_template("index.html", **context)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
