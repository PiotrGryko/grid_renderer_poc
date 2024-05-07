- Mouse scroll to zoom
- Mouse drag to move the scene
- Press C to change color

Loading hugging face model: 

    app = OpenGLApplication()
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    app.start(model)

