"""
Main App Runner
"""
from flask import Flask

app=Flask(__name__)
@app.route("/")
def greet():
    return "Welcome To My App"
app.run(host="0.0.0.0",port="8080")
    