# import functions_framework
from fastapi import FastAPI
import gradio as gr
import os
import openai
import uvicorn
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

def get_completion_from_messages(messages, 
                                 model="gpt-3.5-turbo", 
                                 temperature=0, 
                                 max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
        max_tokens=max_tokens, # the maximum number of tokens the model can ouptut 
    )
    return response.choices[0].message["content"]


product_information="""

Products name, year and price:
Lexus RX 2022 $30,000
Lexus NX 2023 $43,000
Lexus IS 2020 $23,000
Lexus GX 2023 $43,000

Services available at the dealership:
Leasing a new car
Buying a new car
Buying a pre-owned car
Car inspection and repair

"""

def process_user_message(user_input, all_messages, debug=False):
    delimiter = "```"
    # Step 4: Answer the user question
    system_message = f"""
    You are a customer service assistant for a large car dealership. \
    Respond in a friendly and helpful tone, with concise answers from the relevant information available. \
    Make sure to ask the user relevant follow-up questions.
    """
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"},
        {'role': 'assistant', 'content': f"Relevant product and service information:\n{product_information}"}
    ]

    final_response = get_completion_from_messages(all_messages + messages)
    if debug:print("Step 4: Generated response to user question.")
    all_messages = all_messages + messages[1:]
    
    return final_response, all_messages
    

app = FastAPI()

@app.get('/')
def root():
    return {"message": "hello from chatbot! Redirect to /chatbot"}


context = [{'role':'system', 'content':"You are Service Assistant"}]
chat_history = []

print("\n===chatbot started======\n")
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history):
        global context
        response, context = process_user_message(message, context, debug=False)
        context.append({'role':'assistant', 'content':f"{response}"})
        chat_history.append((message, response))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
gr.mount_gradio_app(app, demo, path="/chatbot")



if __name__ == "__main__":
    print("\n======api started to redirect=====\n")
    uvicorn.run(app, host='0.0.0.0', port=8080)