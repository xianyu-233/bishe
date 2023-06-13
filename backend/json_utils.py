import os
import json

LOGS_DIR = "./history/dialogue_cache.json"

# 写入历史消息的实体
def dump_user_dialogue_context(data):
    path = os.path.join(LOGS_DIR)
    with open(path, 'w', encoding='utf8') as f:
        f.write(json.dumps(data, sort_keys=True, indent=4,
                           separators=(', ', ': '), ensure_ascii=False))


# 读取历史消息的实体
def load_user_dialogue_context():
    path = os.path.join(LOGS_DIR)
    if not os.path.exists(path):
        return {"choice_answer":"hi，机器人小智很高心为您服务","slot_values":None}
    else:
        with open(path, 'r', encoding='utf8') as f:
            data = f.read()
            return json.loads(data)

# 聊天结束后删除对话缓存
def delete_user_dialogue_context():
    os.remove(LOGS_DIR)