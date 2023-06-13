import random

from model import CLFModel, MedicalNerModel, BertIntentModel
from config import *
from py2neo import Graph
from json_utils import load_user_dialogue_context


clf_model = CLFModel()
ner_model = MedicalNerModel()
intent_model = BertIntentModel()

graph = Graph('http://localhost:7474/', auth=("neo4j", "jklnm753"))

# 判断是什么类型的的聊天
def classifier(text):
    return clf_model.predict(text)

# 闲聊模块
def gossip_robot(intent):
    return random.choice(
        gossip_corpus.get(intent)
    )

# 识别实体
def entity_recognizition(text):
    msg = []
    msg.append(text)
    entities_info = ner_model.predict(msg)
    return entities_info

# 识别聊天目的模块
def intent_recognizition(text):
    return intent_model.predict(text)

#语义解析(语义槽填槽)
def semantic_parser(text):
    # 聊天目的识别
    intent_rst = intent_recognizition(text)
    # 识别到其他情况(如意图为其他，完全识别不出实体)
    if intent_rst.get("name") == "其他":
        return semantic_slot.get("unrecognized")
    # 实体识别
    slot_rst = entity_recognizition(text)
    print("实体：", slot_rst)

    # 获取目的类型的模板
    slot_info = semantic_slot.get(intent_rst.get("name"))
    # 填槽
    # 插槽类型
    slots = slot_info.get("slot_list")
    slot_values = {}
    for slot in slots:
        slot_values[slot] = None
        # 填充实体
        for ent_info in slot_rst:
            for e in ent_info["entities"]:
                if slot.lower() == e['type']:
                    # 标准化实体(纠错)
                    slot_values[slot] = entity_link(e['word'], e['type'])
                # 对实体为symptom的进行实体Disease映射
                elif slot.lower() != e['type']:
                    slot_values[slot] = entity_link(e['word'], e['type'])

    if len(slot_rst) == 0:
        #读取上下文的实体
        last_slot_values = load_user_dialogue_context()["slot_values"]
        for k in slot_values.keys():
            if slot_values[k] is None:
                slot_values[k] = last_slot_values.get(k, None)

    # 将实体填入槽中
    slot_info["slot_values"] = slot_values

    # 根据意图强度来确认回复策略
    conf = intent_rst.get("confidence")
    if conf >= intent_threshold_config["accept"]:
        slot_info["intent_strategy"] = "accept"
    elif conf >= intent_threshold_config["deny"]:
        slot_info["intent_strategy"] = "clarify"
    else:
        slot_info["intent_strategy"] = "deny"

    print("插槽：",slot_info)
    return slot_info

# 根据语义槽进行回复
def get_answer(slot_info):
    # 数据库查询语句
    cql_template = slot_info.get("cql_template")
    # 回复模板
    reply_template = slot_info.get("reply_template")
    # 题问模板
    ask_template = slot_info.get("ask_template")
    # 实体槽值
    slot_values = slot_info.get("slot_values")
    # 意图
    strategy = slot_info.get("intent_strategy")


    # 如果slot_values为空
    if not slot_values:
        return slot_info
    # 遇到肯定回答的情况
    if strategy == "accept":
        cql = []
        if isinstance(cql_template, list):
            for cqlt in cql_template:
                cql.append(cqlt.format(**slot_values))
        else:
            cql = cql_template.format(**slot_values)
        answer =neo4j_searcher(cql)
        # 如果查询失败
        if len(answer)==0 or answer=="None":
            slot_info["reply_answer"] = "对不起，我还未能学会回答该问题的知识"
        else:
            pattern = reply_template.format(**slot_values)
            slot_info["reply_answer"] = pattern + answer
    elif strategy == "clarify":
        # 澄清用户是否问该问题
        pattern = ask_template.format(**slot_values)
        slot_info["reply_answer"] = pattern
        # 得到肯定意图后给用户回复
        cql = []
        if isinstance(cql_template, list):
            for cqlt in cql_template:
                cql.append(cqlt.format(**slot_values))
        else:
            cql = cql_template.format(**slot_values)
        answer = neo4j_searcher(cql)
        if not answer:
            slot_info["reply_answer"] = "对不起，我还未能学会回答该问题的知识"
        else:
            pattern = reply_template.format(**slot_values)
            slot_info["choice_answer"] = pattern + answer
    elif strategy == "deny":
        slot_info["reply_answer"] = slot_info.get("deny_response")
    return slot_info

# 查询数据库
def neo4j_searcher(cql_list):
    ress = ""
    # 判断cql语句是否为列表类型
    if isinstance(cql_list, list):
        for cql in cql_list:
            rst = []
            # 返回数据的字典清单
            data = graph.run(cql).data()
            if not data:
                continue
            for d in data:
                d = list(d.values())
                if isinstance(d[0], list):
                    rst.extend(d[0])
                else:
                    rst.extend(d)

            data = "、".join([str(i) for i in rst])
            ress += data+"\n"
    else:
        data = graph.run(cql_list).data()
        if not data:
            return ress
        rst = []
        for d in data:
            d = list(d.values())
            if isinstance(d[0], list):
                rst.extend(d[0])
            else:
                rst.extend(d)
        data="、".join([str(i) for i in rst])
        ress +=data
    return ress

# 实体标准化（对错写，误拼等问题进行矫正）
def entity_link(mention,etype):
    return mention

# 构建机器人
def medical_robot(text):
    semantic_slot = semantic_parser(text)
    answer = get_answer(semantic_slot)
    return answer

