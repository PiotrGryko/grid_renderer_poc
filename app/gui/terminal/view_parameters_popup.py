import imgui


class ParametersPopup:
    def __init__(self, config):
        self.parameter_values = {}
        self.config = config

    def render(self):
        if self.config.model_parser.pipeline_task.task.is_none():
            return
        parameters_dict = self.config.model_parser.pipeline_task.task.get_parameters()

        if len(parameters_dict) == 0:
            return

        # Create a button that toggles the visibility of the parameters window
        if imgui.button("Parameters"):
            imgui.open_popup("ParametersPopup")

        if imgui.begin_popup("ParametersPopup"):
            imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (10, 10))
            imgui.begin_child("ParameterInputs", border=True, width=500, height=200)

            for param_name, param_info in parameters_dict.items():

                if param_name == "forward_params" or param_name == "generate_kwargs":
                    continue
                    forward_params = self.config.model_parser.pipeline_task.forward_pass_parameters

                    imgui.text("forward_params:")
                    for key, value in forward_params.items():
                        imgui.text(str(key))
                        imgui.same_line()
                        imgui.text(str(value))
                    continue

                param_type = param_info['type']
                is_optional = param_info['optional']
                default_value = param_info['default']
                if isinstance(param_type, tuple):
                    param_type = param_type[0]
                if not is_optional:
                    continue

                imgui.text(f"{param_name} (Optional, Default: {default_value}, Type: {param_type.__name__})")

                # Initialize parameter value with default if not already set
                if param_name not in self.parameter_values:
                    self.parameter_values[param_name] = default_value

                param_value = self.parameter_values[param_name]
                # Display input fields based on parameter type
                if param_type is bool:
                    _, self.parameter_values[param_name] = imgui.checkbox(f"##{param_name}",
                                                                          param_value)
                elif param_type is int:
                    _, self.parameter_values[param_name] = imgui.input_int(f"##{param_name}",
                                                                           param_value if param_value else 0)
                elif param_type is float:
                    _, self.parameter_values[param_name] = imgui.input_float(f"##{param_name}",
                                                                             param_value if param_value else 0)
                elif param_type is str:
                    _, self.parameter_values[param_name] = imgui.input_text(f"##{param_name}",
                                                                            self.parameter_values[param_name] if
                                                                            self.parameter_values[param_name] else "",
                                                                            256)
                elif param_type is list:
                    imgui.text(f"##{param_name} (list input)")
                    # Handling list input as needed
                else:
                    imgui.text(f"##{param_name} (unsupported type: {param_type})")

                imgui.separator()

            if imgui.button("Close"):
                imgui.close_current_popup()

            imgui.end_child()
            imgui.pop_style_var(1)
            imgui.end_popup()

    def get_values(self):
        return self.parameter_values
