"""
Gradio Wrapper for AskLAQ2 Application
This integrates the Flask app with Gradio for better deployment
"""

import gradio as gr
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the Flask app
from app import app, get_answer, load_data

# Load data on startup
print("Loading dataset and embeddings...")
dataset, question_embeddings, model = load_data()
print("Data loaded successfully!")

# Create Gradio interface
def gradio_get_answer(question, history=None):
    """Wrapper function for Gradio interface"""
    try:
        answer = get_answer(question, dataset, question_embeddings, model)
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="AskLAQ2 - Local Q&A System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎯 AskLAQ2 - Local Q&A System")
    gr.Markdown("### Ask questions about your dataset locally")
    
    with gr.Row():
        with gr.Column(scale=2):
            question_input = gr.Textbox(
                label="Your Question",
                placeholder="Type your question here...",
                lines=3
            )
            submit_btn = gr.Button("Get Answer", variant="primary")
        
        with gr.Column(scale=3):
            answer_output = gr.Textbox(
                label="Answer",
                placeholder="Answer will appear here...",
                lines=8,
                interactive=False
            )
    
    # Examples
    examples = gr.Examples(
        examples=[
            ["What is the main topic of this dataset?"],
            ["Can you summarize the key information?"],
            ["What patterns can you identify in the data?"]
        ],
        inputs=question_input,
        label="Try these examples"
    )
    
    # Footer
    gr.Markdown("---")
    gr.Markdown("**Note:** This application runs completely offline on your local machine.")
    
    # Connect button
    submit_btn.click(
        fn=gradio_get_answer,
        inputs=question_input,
        outputs=answer_output
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
