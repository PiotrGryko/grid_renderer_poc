from transformers import AutoModelForCausalLM

from app.gl.n_opengl import OpenGLApplication


def from_model():
    app = OpenGLApplication()

    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)
    app.start(model, save_mem_file=False, load_mem_file=False)


def from_memfile():
    app = OpenGLApplication()
    app.start(None, save_mem_file=False, load_mem_file=True)


if __name__ == "__main__":
    from_model()
    #from_memfile()
