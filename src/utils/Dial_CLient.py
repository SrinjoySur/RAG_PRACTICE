from openai import AzureOpenAI
from dotenv import load_dotenv
from typing import Optional,List,Dict,Any
import os
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
    filename=log_dir / f"log_{log_timestamp}.txt"
)
logger = logging.getLogger(__name__)
_=load_dotenv()
class DIALCLIENT:
    def __init__(self,api_key:Optional[str]=None,model:Optional[str]="gpt-4") -> None:
        self.api_key=api_key or os.getenv("DIAL_API_KEY","<YOUR_API_KEY_HERE>")
        self.model=model
        self.endpoint=os.getenv("DIAL_ENDPOINT","<YOUR_ENDPOINT>")
        self.api_version="2024-02-01"
        try:
            self.client=AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.endpoint,
                api_version=self.api_version
            )
            if not self.api_key or self.api_key=="<YOUR_API_KEY_HERE>":
                print("Error")
                logger.error("[ERROR] Dial Api Key Not Found.")
                self.client=None
            else:
                logger.info("[OK] DIAL client initialized successfully")
        except Exception as e:
            logger.error(f"[ERROR] Error the Dial CLient Could not be initialized due to exception:{e}")
            self.client=None
    def get_completion(self,messages:List[Dict[str,str]],model:Optional[str]="gpt-4")->str:
        if not self.client:
            return "[ERROR] Dial Client Not Initialized!!!"
        try:
            response=self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=float(os.getenv("LLM_TEMPERATURE","0.1"))
            )
            content=response.choices[0].message.content
            return content if content is not None else "[ERROR] No Response"
        except Exception as e:
            logger.error(f"[ERROR] Exception Occured at get_completion():{e}")
            return f"[ERROR] Exception Occured at get_completion():{e}"
def test_dial_connection():
        logger.info("Testing Dial Connection....")
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
            return True
        else:
            logger.error("[ERROR] Dial Client Could not be initialized.")
            return False
if __name__=="__main__":
    test_dial_connection()