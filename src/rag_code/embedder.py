import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.embeddings import Embeddings
from dotenv import load_dotenv,find_dotenv
import psycopg2

load_dotenv()
os.getenv('HF_API_KEY')
os.getenv('DIAL_API_KEY')
#model = HuggingFaceBgeEmbeddings(model="BAAI/bge-m3",huggingfacehub_api_token=hf_api_token)
model=HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
document=WebBaseLoader(web_path="https://jayant017.medium.com/rag-using-langchain-part-5-hypothetical-document-embeddings-hyde-050f57dfc252").load()
pages=[]
for t in document:
    pages.append(t.page_content)
embeddings=model.embed_documents(pages)
print(embeddings)

