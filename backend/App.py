import os

from modules import classifier, gossip_robot
from modules import medical_robot

from json_utils import dump_user_dialogue_context, load_user_dialogue_context, delete_user_dialogue_context

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# 设置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def text_replay(msg):
    # 解析用户意图
    user_intent = classifier(msg)
    print("聊天意图：",user_intent)
    # 闲聊
    if user_intent in ["greet", "goodbye", "deny", "isbot"]:
        reply = gossip_robot(user_intent)
        if user_intent == 'goodbye':
            delete_user_dialogue_context()
    # 用户表示肯定，读取上下文的实体
    elif user_intent =="accept":
        reply = load_user_dialogue_context()
        reply = reply.get("choice_answer")
    # 其他情况
    else:
        reply = medical_robot(msg)
        print("reply_else:", reply)
        if reply["slot_values"]:
            dump_user_dialogue_context(reply)
        reply = reply.get("reply_answer")

    return reply

@app.get("/{a}")
async def regist(a):
    while(1):
        reply = text_replay(a)
        if reply==None:
            reply="对不起，我没有明白你说的意思"
        print(reply)
        return reply


if __name__ == '__main__':
    uvicorn.run(app)