import json


class FileWriter:
    def write_to_file(ticketID, content):
        with open("output/" + str(ticketID) + ".json", 'w') as f:
            f.write(json.dumps(content))

    def read_from_file(ticketID):
        data = ""
        with open("output/" + str(ticketID) + ".json") as f:
            data = json.load(f)
        return data
