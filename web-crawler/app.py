from flask import Flask, jsonify, render_template, request
import lucene
from indexer import search

app = Flask(__name__)
lucene.initVM()


@app.get("/")
def home():
    return render_template("search.html")

@app.get("/api/search")
def search_api():
    lucene.getVMEnv().attachCurrentThread()
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": []})

    try:
        results = search(query=query, top_n=10)
        return jsonify({"results": results})
    except Exception as exc:
        return jsonify({"error": f"Search failed: {exc}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)