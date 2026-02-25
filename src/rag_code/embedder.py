import os
from abc import ABC,abstractmethod
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader,UnstructuredFileLoader
from langchain_core.documents import Document
from typing import Optional,List,Any
from dotenv import load_dotenv,find_dotenv
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
    filename=log_dir / f"embedder_log_{log_timestamp}.txt"
)
logger = logging.getLogger(__name__)

_=load_dotenv()

class Embedder(ABC):
    def get_web_list_document(self,web_path:Optional[str]=None)->List[Document]:
        document= WebBaseLoader(web_path=web_path or "https://www.espn.com/").load()
        return document
    def get_local_list_document(self,file_path:str,mode:Optional[str]="elements",strategy:Optional[str]="fast")->List[Document]:
        document=UnstructuredFileLoader(file_path=file_path,mode=mode or "elements", strategy=strategy)
        return document.load()
    def get_list_document_contents(self,document:List[Document])->List[str]:
        pages=[]
        for text in document:
            pages.append(text.page_content)
        return pages
    def print_doc_embeddings(self,embeddings):
        print(embeddings)
    @abstractmethod
    def get_embeddings_of_document_contents(self,pages:List[str])->List[List[float]]:
        pass
class HFEmbedder(Embedder):
    def __init__(self,api_key:Optional[str]=None,model_name:Optional[str]="BAAI/bge-m3") -> None:
        self.api_key=api_key or os.getenv("HF_API_KEY","<YOUR_HF_API_KEY>")
        self.model_name=model_name
        try:
            self.client=HuggingFaceEmbeddings(
                model_name=self.model_name
            )
            if not self.api_key or self.api_key=="<YOUR_HF_API_KEY>":
                logger.error(f"[ERROR] HF Initialization api key is incorrect:{self.api_key}")
                self.client=None
            else:
                logger.info("[OK] HF Client Initialized Successfully")
        except Exception as e:
            logger.error(f"[ERROR] HF Embedder initialization has encountered exception:{e}")
            self.client=None
    def get_embeddings_of_document_contents(self,pages:List[str])->List[List[float]]:
        """
        Returns embeddings for a list of document pages using the Hugging Face
        client. Logs an error if the client is not initialized or if an
        exception occurs. Returns a list of embeddings or None on failure.
        """
        try:
            if not self.client:
                logger.error("[ERROR]  HF Client not Initialized")
                return [[]]
            else:
                return self.client.embed_documents(pages)
        except Exception as e:
            logger.error(f"[ERROR] HF Embeddings get_embeddings_of_document_contents() has encountered an exception:{e}")
            return [[]]
class DialEmbedder(Embedder):
    def __init__(self,api_key:Optional[str]=None,model_name:Optional[str]="text-embedding-3-small-1") -> None:
        self.api_key=api_key or os.getenv("DIAL_API_KEY","<YOUR_DIAL_API_KEY>")
        self.model_name=model_name
        self.endpoint=os.getenv("DIAL_ENDPOINT")
        self.api_version="2024-02-01"
        try:
            self.client=AzureOpenAIEmbeddings(
                api_key=self.api_key,
                azure_endpoint=self.endpoint,
                api_version=self.api_version,
                model=self.model_name or "text-embedding-3-small-1"
                #chunk_size=100
            )
            if not self.api_key or self.api_key=="<YOUR_DIAL_API_KEY>":
                print("Error")
                logger.error("[ERROR] Dial Api Key Not Found.")
                self.client=None
            else:
                logger.info("[OK] DIAL client initialized successfully")
        except Exception as e:
            logger.error(f"[ERROR] Error the Dial CLient Could not be initialized due to exception:{e}")
            self.client=None
    def get_embeddings_of_document_contents(self,pages:List[str])->List[List[float]]:
        try:
            if not self.client:
                logger.error("Azure Embbeder Client Not Instantiated.")
                return [[]]
            else:
                return self.client.embed_documents(pages)
        except Exception as e:
            logger.error(f"[ERROR] Exception occured at Azure Embedding get_embeddings_of_document_contents:{e}")
            return [[]]
def run_embedding_process(embedder:Optional[str]="HF"):
    aembedder=vars
    if embedder=="HF":
        aembedder=HFEmbedder()
    else:
        aembedder=DialEmbedder()
    if not aembedder.client:
        logger.error("[ERROR] Emmbeder Client could not be initialized correctly")
    #document=aembedder.get_web_list_document("https://jayant017.medium.com/rag-using-langchain-part-5-hypothetical-document-embeddings-hyde-050f57dfc252")
    document=aembedder.get_local_list_document("src/data/rag_sample_qas_from_kis.csv")
    pages=aembedder.get_list_document_contents(document)
    embeddings=aembedder.get_embeddings_of_document_contents(pages)
    logger.info(f"[OK] Response Recieved:{embeddings}")
    aembedder.print_doc_embeddings(embeddings)
if __name__=="__main__":
    run_embedding_process()
