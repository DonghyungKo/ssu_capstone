import json

# json 파일을 저장하는 함수
def save_json(dic, path_to_file):
    return json.dump(dic, open(path_to_file, 'w', encoding='utf-8'), ensure_ascii=False)

# json 파일을 읽어오는 함수
def load_json(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as f:
        return json.load(f)
