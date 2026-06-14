import gradio as gr
from query import ask


def handle_query(question):
    result = ask(question)
    answer = result["answer"]
    sources = "\n".join(f"- {source}" for source in result["sources"])
    return answer, sources


with gr.Blocks() as demo:
    gr.Markdown("# The Unofficial Guide")
    gr.Markdown("Ask questions about student professor reviews.")

    question = gr.Textbox(label="Your question")
    button = gr.Button("Ask")

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Sources", lines=5)

    button.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])


demo.launch()