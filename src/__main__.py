# from fastapi import FastAPI

# app=FastAPI(description="""
#             Sample App Implementation.
#             """)
# @app.get("/greet")
# def greet():
#     return "Welcome To My App"
from flask import Flask,render_template
from utils.Dial_CLient import DIALCLIENT
#from api.Dial_Example_Implementation import example_dial_implementation
import logging
from pathlib import Path
from datetime import datetime
log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_dir = Path(__file__).resolve().parent.parent / "logs"

# Ensure the logs directory exists
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_dir / f"main_app_log_{log_timestamp}.txt"
)
logger = logging.getLogger(__name__)
app=Flask(__name__)
@app.route("/")
def greet():
    logger.info("Greet Endpoint hit!!!")
    return "Welcome To My App"
@app.route("/dial_client")
def Test_Dial():
    client=DIALCLIENT()
    if not client.client:
        logger.error("Dial CLient Not Initialized")
        return False
    test_messages=[
        {"role":"user","content":"Explain the concept of 'technical debt' in one sentence."}
    ]
    response=client.get_completion(test_messages)
    logger.info(f"Test Response:{response}")
    if "ERROR" not in response:
        logger.info("[OK] Dial Client Connection Successful.")
        return response
    else:
        logger.error("[ERROR] Dial Client Could not be initialized.")
@app.route("/dial_impl")
def example_dial_implementation():
    client=DIALCLIENT()
    if not client.client:
        logger.error("Dial Client not Initialized")
    prompt=input("Enter Your Prompt:")
    message=[{"role":"user","content":prompt}]
    response=client.get_completion(messages=message)
    logger.info(f"[OK] Response Recieved:{response}")
    return response

app.run(host="0.0.0.0",port="8080")
    