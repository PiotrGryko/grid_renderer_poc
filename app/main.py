from transformers import AutoModelForCausalLM

from app.gl.n_opengl import OpenGLApplication

if __name__ == "__main__":
    app = OpenGLApplication()

    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    app.start(model)
