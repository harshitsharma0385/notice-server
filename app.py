from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)


client = MongoClient("mongodb+srv://harshit3850_db_user:vampiremongo@cluster0.ofot2vd.mongodb.net/?appName=Cluster0")
db = client["notice_board"]
collection = db["notices"]

# Admin Panel

@app.route("/")
def admin():
    notices = list(collection.find().sort("created_at", -1))
    return render_template("admin.html", notices=notices)

#Add notice

@app.route("/add", methods=["POST"])
def add_notice():
    title = request.form["title"]
    description = request.form["description"]
    expiry = datetime.strptime(request.form["expiry"], "%Y-%m-%d")

    notice = {
        "title": title,
        "description": description,
        "expiry": expiry,
        "created_at": datetime.now()
    }

    collection.insert_one(notice)
    return redirect("/")

# Delete Notice

@app.route("/delete/<id>")
def delete_notice(id):
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
            "created_at": notice["created_at"].strftime("%Y-%m-%d %H:%M")
        }

        if "expiry" in notice:
            formatted_notice["expiry"] = notice["expiry"].strftime("%Y-%m-%d")

        formatted_notices.append(formatted_notice)

    return jsonify(formatted_notices)

    

if __name__ == "__main__":
    app.run(debug=True)