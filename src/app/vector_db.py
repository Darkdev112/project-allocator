import time
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore 
from langchain_huggingface import HuggingFaceEmbeddings
from config import Config

def create_store():
    pinecone = Pinecone(api_key=Config.PINECONE_API_KEY)
    index_name = Config.PINECONE_INDEX_NAME

    embedding = HuggingFaceEmbeddings(
        model="sentence-transformers/all-MiniLM-l6-v2"
    )
    
    if not pinecone.has_index(index_name):
        print("Creating Pinecone index...")
        pinecone.create_index(
            name=index_name,
            dimension=384,
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print("Waiting for Pinecone index to be ready...")
        while not pinecone.describe_index(index_name).status.ready:
            time.sleep(1)
        print("Pinecone index is ready.")

    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embedding)
    return vectorstore