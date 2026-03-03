from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os
import cloudinary
import cloudinary.uploader


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["notice_board"]
collection = db["notices"]

# Cloudinary Config
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

# Login Panel

ADMIN_PASSWORD =  os.getenv("ADMIN_PASSWORD")
@app.route("/login", methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login.html", error = "Wrong Password")
    return render_template("login.html")
    # return """
    #     <h2>Admin Login</h2>
    #     <form method="POST">
    #         <input type="password" name="password" placeholder="Enter Password" required>
    #         <button type="submit">Login</button>
    #     </form>
    # """

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# Admin Panel

@app.route("/")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))
    notices = list(collection.find().sort("created_at", -1))
    return render_template("admin.html", notices=notices)

#Add notice

@app.route("/add", methods=["POST"])
def add_notice():
    if not session.get("admin"):
        return redirect(url_for("login"))
    title = request.form["title"]
    description = request.form["description"]
    image = request.files.get("image")
    image_url = ""

    #Upload image to cloudinary
    if image and image.filename != "":
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result["secure_url"]

    notice = {
        "title": title,
        "description": description,
        "image_url": image_url,
        "created_at": datetime.now()
    }

    collection.insert_one(notice)
    return redirect("/")

    
# Delete Notice

@app.route("/delete/<id>")
def delete_notice(id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    collection.delete_one({"_id": ObjectId(id)})
    return redirect("/")

#API for MagicMirror

@app.route("/api/notices")
def get_notices():
    notices = list(collection.find().sort("created_at", -1))

    formatted_notices = []

    for notice in notices:
        formatted_notice = {
            "_id": str(notice["_id"]),
            "title": notice.get("title", ""),
            "description": notice.get("description", ""),
            "image_url": notice.get("image_url", ""),
            "created_at": notice["created_at"].strftime("%Y-%m-%d %H:%M")
        }

        # if "expiry" in notice:
        #     formatted_notice["expiry"] = notice["expiry"].strftime("%Y-%m-%d")

        formatted_notices.append(formatted_notice)

    return jsonify(formatted_notices)

    

if __name__ == "__main__":
    app.run(debug=True)