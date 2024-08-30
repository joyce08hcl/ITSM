from pymongo import MongoClient
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()

import os
from langchain_openai import OpenAI,ChatOpenAI 


os.environ["OPENAI_API_BASE"] ='http://10.35.151.101:8001/v1'
os.environ["OPENAI_API_KEY"] = "sk-1234"
os.environ["OPENAI_MODEL_NAME"] = 'llama-3.1-70b'

model = ChatOpenAI(
    model="llama-3.1-70b",
    temperature=0.3,
    max_tokens=3000,
)

client = MongoClient(os.getenv("MONGO_URI"))
dbName = "itsm_database"
collectionName = "ticket_data"
collection = client[dbName][collectionName]

loader = DirectoryLoader('./sample_files', glob='./*.txt', show_progress=True)
data = loader.load()

embeddings = OpenAIEmbeddings(model="llama-3.1-70b", api_key="sk-1234", base_url="http://10.35.151.101:8001/v1")
vectorStore = MongoDBAtlasVectorSearch.from_documents(data, embeddings, collection=collection)



def query_data(query):
    # Retrieve all relevant documents matching the query
    docs = vectorStore.similarity_search(query, K=10)  # Adjust K based on the expected number of relevant chunks
    
    # Concatenate the chunks
    concatenated_text = " ".join([doc.page_content for doc in docs])

    # Run the concatenated text through the LLM for a final answer
    llm = OpenAI(model="llama3", api_key="sk-1234", base_url="http://10.35.151.101:8001/v1")
    retriever = vectorStore.as_retriever()
    qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=retriever)

    try:
        retriever_output = qa.invoke(concatenated_text)
        final_output = retriever_output['result']
    except Exception as e:
        print(f"Error during QA retrieval: {str(e)}")
        final_output = "Error processing the query."

    return concatenated_text, final_output


def extract_ticket_details(doc):
    """Extract ticket details from the page content of a document."""
    lines = doc.page_content.split('\n')
    ticket_details = {}
    current_key = None
    
    for line in lines:
        if ': ' in line and not line.startswith('-'):
            key, value = line.split(': ', 1)
            current_key = key.strip()
            ticket_details[current_key] = value.strip()
        elif current_key and line.startswith('-'):
            # Handling comments or possible solutions
            if current_key not in ticket_details:
                ticket_details[current_key] = line.strip()
            else:
                ticket_details[current_key] += f"\n{line.strip()}"
        elif current_key:
            # Append to the current key for multi-line values
            ticket_details[current_key] += f" {line.strip()}"
    
    return ticket_details


#### all top results without K i.e all matching data

query = "Was there any issue regarding slow internet speed in the office? If yes, what were the possible solutions?"
docs = vectorStore.similarity_search(query, K=1)  # Adjust K based on the expected number of relevant chunks

# Extracting and printing only the ticket details
for doc in docs:
    ticket_details = extract_ticket_details(doc)
    print(ticket_details)