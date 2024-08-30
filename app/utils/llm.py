import os
# from langchain_groq import ChatGroq
from langchain_openai import OpenAI,ChatOpenAI
# Set your API key if not set as an environment variable


os.environ["OPENAI_API_BASE"] ='http://10.35.151.101:8001/v1'
os.environ["OPENAI_API_KEY"] = "sk-1234"
# os.environ["OPENAI_MODEL_NAME"] = 'ibm-llama3-70b'

# llm_model = ChatOpenAI(
#     model_name="ibm-llama3-70b",  # Example model, replace with your model
#     temperature=0.3,
#     max_tokens=8000,
# )


# # Initialize the Groq model
# llm_model2 = ChatOpenAI(
#     model="ibm-llama3-70b",  # Example model, replace with your model
#     temperature=0.3,
#     max_tokens=8000,

# )

# os.environ["OPENAI_API_BASE"] ='https://api.groq.com/openai/v1'
# os.environ["OPENAI_API_KEY"] = "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"
from langchain_openai import ChatOpenAI

nijapi="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"
heapi="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"
weapi="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"

# Initialize the Groq model
llm_model2 = ChatOpenAI(
    model="ibm-llama3-1-70b",
    temperature=0.3,
    max_tokens=3000,
    # base_url="https://api.groq.com/openai/v1",
    # api_key=heapi,
    

)

# Initialize the Groq model
llm_model_network = ChatOpenAI(
    model="ibm-llama3-1-70b",
    temperature=0.3,
    max_tokens=3000,
    
    

)
llm_model_security = ChatOpenAI(
    model="llama3-groq-70b-8192-tool-use-preview",  # Example model, replace with your model
    temperature=0.3,
    max_tokens=000,
    base_url="https://api.groq.com/openai/v1",
    api_key=heapi,

)
llm_model_devops = ChatOpenAI(
    model="llama3-groq-70b-8192-tool-use-preview",  # Example model, replace with your model
    temperature=0.3,
    max_tokens=8000,
    base_url="https://api.groq.com/openai/v1",
    api_key=weapi,

)


import os

from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_BASE"] ='http://10.35.151.101:8001/v1'
os.environ["OPENAI_API_KEY"] = "sk-1234"
os.environ["OPENAI_MODEL_NAME"] = 'ibm-llama3-1-70b'

model = ChatOpenAI(
    model="ibm-llama3-1-70b",
    temperature=0.3,
    max_tokens=3000,
)


