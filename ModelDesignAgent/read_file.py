


def read_model_tools(input_model_name):
    model_code = ""
    model_name = input_model_name
    if model_name == "boost converter" or model_name == "Boost converter" or model_name == "boost" or model_name == "Boost":
        file_path = "cpl_boost.mo"
    with open(file_path, 'r') as f:
        model_code = f.read()
        return model_code

def write_model_tools(input):
    model_name = input.model_name
    model_code = input.model_code
    file_path = f"{model_name}.mo"
    with open(file_path, 'w') as f:
        f.write(model_code)
    return file_path

print(read_model_tools("Boost converter"))

