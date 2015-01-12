from flask import Flask, render_template

app = Flask(__name__)

import os

env = "development"

app.config.from_object("server_config.Config" + env.capitalize())

@app.route("/")
def index():
    return render_template(
            "index.html",
            ctx={
                "realm": "XX",
                "roles": ["ljop", "ljadmin"],
                "role": "ljadmin",
                "role_default": "ljop"})
