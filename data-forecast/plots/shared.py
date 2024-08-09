import json

def load_leaderboard(file_path, number_of_lines_to_read = -1):

    with open(file_path, 'r') as file:
        data = file.read()

    cost_dict = json.loads(data)

    if number_of_lines_to_read != -1:
        cost_dict = {k: cost_dict[k] for k in list(cost_dict)[:number_of_lines_to_read]}

    return cost_dict


# Aceder aos valores do dicionário
#for id, cost in cost_dict.items():
#    print(f'ID: {id}, Cost: {cost}')
