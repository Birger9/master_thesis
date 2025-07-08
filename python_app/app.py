import gradio as gr
from NL_to_SPARQL import translate_nl_to_sparql
from SPARQL_to_NL import translate_sparql_to_nl

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        label="SPARQL Assistant",
        type="messages",
        height=400
    )
    msg = gr.Textbox(placeholder="Ask a question...")
    one_shot_cb = gr.Checkbox(label="Use one shot example?", value=False)

    def pipeline_chat(user_message, one_shot, history):
        history = history or []
        
        # Show the user’s message in the Chat UI.
        history.append({"role": "user", "content": user_message})
        
        # Translate the user question into a SPARQL query.
        sparql = translate_nl_to_sparql(user_message, one_shot=one_shot)

        # Show the generated query in the Chat UI.
        history.append({"role": "user", "content": f"Generated Query\n\n{sparql}\n\n"})

        # Translate the SPARQL query to a natural language translation.
        #nl_explanation = translate_sparql_to_nl(sparql)

        # Show the natural language translation in the Chat UI.
        #history.append({"role": "assistant", "content": f"Natural Language Translation\n\n{nl_explanation}"})
        return "", history

    msg.submit(pipeline_chat, [msg, one_shot_cb, chatbot], [msg, chatbot])
    demo.launch()
