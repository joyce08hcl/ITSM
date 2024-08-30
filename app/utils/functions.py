import ast
import re
import json
# from langchain_openai import OpenAI,ChatOpenAI 
from langchain_community.llms import OpenAI
from langchain.prompts import ChatPromptTemplate
from pymongo import MongoClient
from utils.models import model, search
from langchain_community.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from dotenv import load_dotenv
from ssl import CERT_NONE
from utils.models import vectorStore


load_dotenv()



def sentiment_analyzer(query, person_name="Unknown", person_id_no="Unknown"):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an assistant whose job is to analyze the sentiment of the user's query. 
                Your task is to determine whether the sentiment of the query is positive, neutral, or negative, 
                and also provide a sentiment score. Consider the intent, tone, and implications of the query when 
                determining the sentiment. A positive sentiment often reflects satisfaction, approval, or optimistic intent; 
                a neutral sentiment reflects a factual or directive tone without strong emotional content; a negative sentiment 
                reflects dissatisfaction, concern, or a pessimistic intent.

                If the query describes an action or intent to perform a task (such as implementing a system or taking steps to improve something), 
                classify it as neutral unless there is an explicit expression of positive or negative emotion.

                Please return the output in the following dictionary format and only return the result:

                {{
                    "sentiment": sentiment (positive, neutral, negative),
                    "sentiment_score": sentiment score (ranging from -1 to +1)
                }}
                
                """,
            ),
            ("human", "{input}"),
        ]
    )



    question = query
    
    chain = prompt | model
    result=chain.invoke(
        {
            "input": question,
            "person_name": person_name,
            "person_id_no": person_id_no,
            "query": question
                    
        }
    )
    nodes_context=result
    return nodes_context


def Query_analysis(user, sap_id, query):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a ITSM assistent whose work is to analyze and summarize the query in the pointer system.
                The user has given you a long query Now you have to analyze the query and give the brief overview of the in the pointer system So that any one could understant it.
                Please return the result in the following dictionary format and only return the result.
                {{
                "summary": generated summarized result
                }}
                """,
            ),
            ("human", "{input}"),
        ]
    )
    question= f"User: {user} with the SAP ID: {sap_id} has the following problem:\n {query}"
    chain = prompt | model
    result=chain.invoke(
        {
             "input": question,
                    
        }
    )
    nodes_context=result
    return nodes_context




def dep_router(user, sap_id, query):
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a assistent whose work is to route the query of the user according to his question 
                possible path available to you are
                1. Human resource
                2. IT Admin
                3. Assest Management
                
                and give the output in the dictionary format and only return the result:
                
                  "department": path_given,
                
                """,
            ),
            ("human", "{input}"),
        ]
    )

    question= f"User: {user} with the SAP ID: {sap_id} has the following problem :\n{query}"
    chain = prompt | model
    result=chain.invoke(
        {
             "input": question,
                    
        }
    )
    nodes_context=result
    return nodes_context




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
           
            if current_key not in ticket_details:
                ticket_details[current_key] = line.strip()
            else:
                ticket_details[current_key] += f"\n{line.strip()}"
        elif current_key:
            
            ticket_details[current_key] += f" {line.strip()}"
    
    return ticket_details



def extract_list_from_string(string):
    match = re.search(r'\[(.*)\]', string, re.DOTALL)
    if match:
        list_str = match.group(0)
        extracted_list = ast.literal_eval(list_str)
        return extracted_list
    else:
        return extract_list_from_string(string)
    



def websearch_solution(query):
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a professional ITSM support Person. 
        Now the user has given some query for which which we have to search on the internet for it's answer
        Now from this query you have to create some websearch questions which the user can search over the internet to get relevant answre regarding the user query
        give 5 questions
        the output should be in the format of  python list ["qustion1", "question2", "question3","question4","question5"]. Only return the list of questions.
            """,
        ),
        ("human", "{input}"),
    ]
    )
    chain = prompt | model
    result=chain.invoke(
        {
            
            "input": f"Give some  websearch question on this query to find the relevant answer, the question is {query}",
        }
    )

    Context=result
    extracted_list = extract_list_from_string(Context)
    questions = extracted_list
    search_results_as_strings = []

    for question in questions:
        result = search.invoke(question)
        result_string = f"\nFAQ: {question}\nAnswer: {result}\n"
        search_results_as_strings.append(result_string)

    final_result_string = "\n".join(search_results_as_strings)
    print(final_result_string)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a professional ITSM person whose task is to provide the solution to the person on the basis text given below
                and for giving the answer you are given a some text to use as refernce to give the anwer the reference text is as {Question_base}
                """,
            ),
            ("human", "{input}"),
        ]
    )

    chain = prompt | model
    result=chain.invoke(
        {
            "Question_base": search_results_as_strings,
            "input": f" Provide the solution to the problem {query} ",
        }
    )

    connections_context=result
    print(connections_context)
    return connections_context



def raise_ticket_format(user, sap_id, query):
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an ITSM assistant whose job is to evaluate responses to user queries and generate a ticket in the appropriate format if the response is not satisfactory.
                You will be given a user's query and the response provided by another system.
                Now you have to generate the ticket from those and also summarize the reponse in pointer and short system
                
                provide the output in the following dictionary format:

                  'Ticket ID': '<Generate a ticket ID>',     
                  'Summary': '<Brief Summary of the Issue>',
                  'User': user,
                  'SAP ID': '<sap_id>',
                  'Query': '<query>',
                  'Description': '<Brief explanation of why the response was not satisfactory>',
                  'Next Steps': '<Suggested next steps for resolution>',
                  'Priority': 'High/Medium/Low'

                only give the output in the python dictionary format no behind the code
                
                """,
            ),
            ("human", "Query: {query}"),
        ]
    )

    chain = prompt | model
    result = chain.invoke(
        {
            "query": query,
        }
    )
    evaluation = result
    print("\n\nTicket Created Successfully!!!")
    print(evaluation)
    return evaluation



def name_sapid(name, sap_id):
    return f"Received name: {name}, SAP ID: {sap_id}"


def main(query, user_name, user_id):
    

    sentiment_data = sentiment_analyzer(query, person_name=user_name, person_id_no=user_id)
    sentiment_dict = json.loads(sentiment_data)
    summarizer = Query_analysis(user_name, user_id, query)
    summarizer = json.loads(summarizer)
    router = dep_router(user_name, user_id, query)
    router = json.loads(router)

    ticket_data = {
        "user": user_name,
        "sap_id": user_id,
        "query": query,
        "sentiment_data": sentiment_dict,
        "summarized_data": summarizer,
        "routed_department": router
    }


    print(ticket_data)

    if router.get("department") == "IT Admin":
        print("\n\nRouting to IT Admin department...")
        print("\nSearching the database for similar issues and solutions...")

        docs = vectorStore.similarity_search(query, K=2)
        K=2
        docs = docs[:K]

    
        ticket_details_list = []
        for doc in docs:
            ticket_details = extract_ticket_details(doc)
            print(ticket_details)
            ticket_details_list.append(ticket_details)

            # if ticket_details_list:
            #     if 'user_option' not in st.session_state:
            #         st.session_state.user_option = "Yes"  # default value

            #     option = st.selectbox("Does the above solutions solve your current issue?", ("Yes", "No"), index=0)
            #     st.session_state.user_option = option

            #     if st.button("Submit Response"):
            #         if st.session_state.user_option.lower() == "yes":
            #             st.markdown("Thank you for reaching out...")
            #         else:
            #             st.info("No issues... Here are some FAQs that could help you.")
            #             response = websearch_solution(query)
            #             st.write(response)

            #             if 'faq_option' not in st.session_state:
            #                 st.session_state.faq_option = "Yes"  # default value

            #             faq_option = st.selectbox("Did these FAQs solve your current issue?", ("Yes", "No"), index=0)
            #             st.session_state.faq_option = faq_option

            #             if st.button("Submit FAQs Response"):
            #                 if st.session_state.faq_option.lower() == 'yes':
            #                     st.markdown("Thank you for reaching out...")
            #                 else:
            #                     st.info("No issues... We have raised a ticket for you.")
            #                     raise_ticket_format(user_name, user_id, query, response)


            # else:
            #     st.write("No issues... Here are some FAQs and Tips that could help you.")
            #     response = websearch_solution(query)
            #     choice2 = st.radio("Did these FAQs solve your current issue?", ("Yes", "No"))
            #     if st.button("Submit FAQs Response"):
            #         if choice2.lower() == 'yes':
            #             st.write("Thank you for reaching out...")
            #         else:
            #             st.write("No issues... We have raised a ticket for you.")
            #             raise_ticket_format(user_name, user_id, query, response)
            

        