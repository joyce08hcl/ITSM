from langchain_groq import ChatGroq
import os
from langchain_community.tools import DuckDuckGoSearchRun
import pymongo
from pymongo import MongoClient
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
# from langchain_openai import OpenAI,ChatOpenAI 
from langchain.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings


search = DuckDuckGoSearchRun()
os.environ["OPENAI_API_BASE"] ='http://10.35.151.101:8001/v1'
os.environ["OPENAI_API_KEY"] = "sk-1234"
os.environ["OPENAI_MODEL_NAME"] = 'llama3'
os.environ["MONGO_URI"] = "mongodb+srv://joycemerin:3aAvXWtBA0CIn1T3@itsm.dgtvy.mongodb.net/?retryWrites=true&w=majority&appName=itsm"

model = OpenAI(
    model="llama3",
    temperature=0.3,
    max_tokens=3000,
)

os.environ["GROQ_API_KEY"] = "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"

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
)

llm2 = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    max_tokens=None,
    timeout=None,
)

print(pymongo.__version__)


client = MongoClient(
    os.getenv("MONGO_URI"),
)

dbName = "itsm_database"
collectionName = "ticket_data"
collection = client[dbName][collectionName]
print(client.server_info())

embeddings = OpenAIEmbeddings(api_key="sk-1234")
vectorStore = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings
)
    