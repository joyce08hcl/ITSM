from flask import Flask, render_template, request, jsonify, session
from utils.functions import name_sapid, sentiment_analyzer, Query_analysis, dep_router, raise_ticket_format, websearch_solution, extract_ticket_details, raise_ticket_format
import os 
import json
from utils.models import vectorStore

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    return render_template('chat.html')



@app.route('/get', methods=['POST'])
def get_bot_response():
    user_msg = request.form.get('msg')
    user_name = session.get('user_name')
    sap_id = session.get('sap_id')
    step = session.get('step', '')

    response = "Sorry, I couldn't understand your request."
    suggestions = ""

    if user_name and sap_id:
        try:
            if step == 'check_solution':
                if user_msg.lower() == "yes":
                    response = "<p>Great! I'm glad the solution was helpful. Do you need any further assistance?</p>"
                    suggestions = "No, thank you\nYes, I have another question"
                    session['step'] = ''  # Clear the step after processing
                elif user_msg.lower() == "no":
                    # If the solution from the database didn't help, run the websearch function
                    response = "<p>I'm sorry that didn't help. Let me search for some FAQs that might help you.</p>"
                    faqs = websearch_solution(session.get('query'))
                    response += f"<h4>FAQs:</h4><p>{faqs}</p>"
                    suggestions = "Yes\nNo"
                    session['step'] = 'check_faq'  # Move to the next step to check FAQs

            elif step == 'check_faq':
                if user_msg.lower() == "yes":
                    response = "<p>Great! I'm glad the FAQ was helpful. Do you need any further assistance?</p>"
                    suggestions = "No, thank you\nYes, I have another question"
                    session['step'] = ''  # Clear the step after processing
                elif user_msg.lower() == "no":
                    # If the FAQs didn't help, raise a ticket
                    response = "<p>I'm sorry that didn't help. I will escalate this to the IT Admin for further assistance. I have also raise a ticket for you with the following details :</p>"
                    ticket = raise_ticket_format(user_name, sap_id, user_msg)
                    print(ticket)
                    response += ticket
                    suggestions = ""  # No further suggestions, end the conversation or offer another option
                    # Code to raise a ticket here...
                    session['step'] = ''  # Clear the step after processing

            else:
                sentiment_data = sentiment_analyzer(user_msg, person_name=user_name, person_id_no=sap_id)
                sentiment_dict = json.loads(sentiment_data)
                summarizer = Query_analysis(user_name, sap_id, user_msg)
                summarizer = json.loads(summarizer)
                router = dep_router(user_name, sap_id, user_msg)
                router = json.loads(router)

                ticket_data = {
                    "user": user_name,
                    "sap_id": sap_id,
                    "query": user_msg,
                    "sentiment_data": sentiment_dict,
                    "summarized_data": summarizer,
                    "routed_department": router
                }

                print("\n\nUser Query Details", ticket_data)

                if router.get("department") == "IT Admin":
                    print("\n\nRouting to IT Admin department...")
                    print("\nSearching the database for similar issues and solutions...")

                    docs = vectorStore.similarity_search(user_msg, K=2)
                    docs = docs[:2]

                    ticket_details_list = []
                    for doc in docs:
                        ticket_details = extract_ticket_details(doc)
                        ticket_details_list.append(ticket_details)
                        print(ticket_details)

                    if ticket_details_list:
                        ticket_details_str = "\n".join([json.dumps(detail, indent=2) for detail in ticket_details_list])
                        
                        session['ticket_details_list'] = ticket_details_list
                        session['query'] = user_msg  # Save the query for later use
                        response = f"Here are some solutions we found for similar issues:\n{ticket_details_str}"
                        suggestions = "Yes\nNo"
                        session['step'] = 'check_solution'  # Mark the step for checking solution

                    else:
                        response = "No similar issues were found in the database. Let me show you some FAQs that might help."
                        faqs = websearch_solution(user_msg)
                        response += f"\nFAQs:\n{faqs}"
                        suggestions = "Yes\nNo"
                        session['step'] = 'check_faq'  # Mark the step for checking FAQs
                        session['faqs'] = faqs  # Save the FAQs in the session

        except json.JSONDecodeError as e:
            response = "There was an error processing your request. Please try again later."
            suggestions = ""
            print(f"JSON decoding error: {e}")

    else:
        response = "Please provide your name and SAP ID first."
        suggestions = ""

    return jsonify({'message': response, 'suggestions': suggestions})




    # response = "This is a dummy response."
    # suggestions = "Suggestion 1\nSuggestion 2\nSuggestion 3"
    # return jsonify({'message': response, 'suggestions': suggestions})


@app.route('/process_selection', methods=['POST'])
def process_selection():
    user_selection = request.form.get('msg')
    current_step = session.get('step')

    if current_step == 'check_solution':
        if user_selection.lower() == 'yes':
            response = "Great! I'm glad the solution worked for you."
            suggestions = ""
        else:
            # Show FAQs if the solution didn't work
            faqs = session.get('faqs')
            if not faqs:  # If FAQs are not already stored, generate them
                user_msg = session.get('query')
                faqs = websearch_solution(user_msg)
                session['faqs'] = faqs

            response = f"Here are some FAQs that might help:\n{faqs}"
            suggestions = "Yes\nNo"
            session['step'] = 'check_faq'  # Move to the FAQ step

    elif current_step == 'check_faq':
        if user_selection.lower() == 'yes':
            response = "Great! I'm glad the FAQs helped."
            suggestions = ""
        else:
            # Raise a ticket if the FAQ didn't help
            user_name = session.get('user_name')
            sap_id = session.get('sap_id')
            user_msg = session.get('query')
            faqs = session.get('faqs')

            # Create a ticket
            ticket = raise_ticket_format(user_name, sap_id, user_msg, faqs)
            print(ticket)
            response = "It seems we need further assistance to solve your issue. A ticket has been raised."
            suggestions = ""

    else:
        response = "I'm not sure how to proceed. Please start again."
        suggestions = ""

    return jsonify({'message': response, 'suggestions': suggestions})


@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.json
    user_name = data['name']
    sap_id = data['sapId']
    result = name_sapid(user_name, sap_id)
    print(result)
    
    # Store data in session
    session['user_name'] = user_name
    session['sap_id'] = sap_id
    session['step'] = 1  # Starting step
    session['query'] = None
    
    return jsonify({'message': 'Data processed successfully', 'result': result})

if __name__ == "__main__":
    app.run(debug=True, port=5004, host='0.0.0.0')
