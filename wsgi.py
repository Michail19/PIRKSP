import os
from flask import jsonify
from app import create_app
from config import Config

app = create_app()


@app.route("/whoami", methods=["GET"])
def whoami():
    return jsonify({
        "hostname": os.getenv("HOSTNAME", "unknown"),
        "version": app.config.get("APP_VERSION"),
        "env": app.config.get("APP_ENV"),
    })


if __name__ == "__main__":
    app.run(
        host=Config.APP_HOST,
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )

    print(f"Starting app version={Config.APP_VERSION}, env={Config.APP_ENV}")
