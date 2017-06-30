import json


def write(name, data):
    if name == "config":
        with open("config.json", "w") as file:
            file.write(json.dumps(data, indent=2))
    elif name == "teams":
        with open("teams.json", "w") as file:
            file.write(json.dumps(data, file, indent=2))
    elif name == "whitelist":
        with open("whitelist.json", "w") as file:
            file.write(json.dumps(data, indent=2))



def load(name):
    if name == "config":
        with open("config.json", "r") as file:
            config = json.load(file)
        return config
    elif name == "teams":
        with open("teams.json", "r") as file:
            teams = json.load(file)
        return teams
    elif name == "whitelist":
        with open("whitelist.json", "r") as file:
            whitelist = json.load(file)
        return whitelist



def add_to_blacklist(blacklist, ID_to_blacklist, name, reason):
    "Adds an ID to the specified blacklist"
    config = load("config")
    config[blacklist][ID_to_blacklist] = {"reason":reason}
    write("config", config)
