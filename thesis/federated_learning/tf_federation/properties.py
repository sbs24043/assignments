import tomli

# Open and read the pyproject.toml
with open("pyproject.toml", "rb") as file:
    custom_params = tomli.load(file)["tool"]["flwr"]["custom_params"]

dataset = custom_params["dataset"]