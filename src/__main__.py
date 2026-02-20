# from fastapi import FastAPI

# app=FastAPI(description="""
#             Sample App Implementation.
#             """)
# @app.get("/greet")
# def greet():
#     return "Welcome To My App"
from flask import Flask

app=Flask(__name__)
@app.route("/")
def greet():
    return "Welcome To My App"
app.run(host="0.0.0.0",port="")
    