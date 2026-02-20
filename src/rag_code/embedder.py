import os
from langchain_huggingface import HuggingFaceEndpointEmbeddings,HuggingFacePipeline
from langchain_community.document_loaders import WebBaseLoader
from dotenv import load_dotenv
import psycopg2
_=load_dotenv()

os.getenv('HF_API_KEY')
os.getenv('DIAL_API_KEY')
model = HuggingFaceEndpointEmbeddings(model="BAAI/bge-m3")
document=WebBaseLoader(web_path="https://jayant017.medium.com/rag-using-langchain-part-5-hypothetical-document-embeddings-hyde-050f57dfc252").load()
pages=[]
for t in document:
    pages.append(t)
embeddings=model.embed_documents(pages)
print(embeddings)
