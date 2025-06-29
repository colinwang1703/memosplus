from config import Config
from hola import Hola
from wrapper import ModelWrapper

import argparse
import random
import time
import urllib3


def main(args):
    # 禁用 TLS 不安全请求警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    cfg = Config(args.compose_file)
    hola = Hola(cfg)
    wrapper = ModelWrapper(cfg)

    hola.second_init()

    # 初始化AI角色
    wrapper.init_chat({
        "role": "system",
        "content": cfg.role_prompt
    }, max_len=5)

    blacklist = {} # 黑名单，存储"备忘录ID": "复活时间"

    print(f"欢迎使用MemosPlus，当前角色: {cfg.role_name} (ID: {cfg.role_id})")


    while True:
        # 0. 检查是否应该"睡觉"
        current_hour = time.localtime().tm_hour
        if current_hour < cfg.role_morning or current_hour >= cfg.role_morning + cfg.role_active_hours:
            print("当前时间不在活跃时间内，休眠中...")
            time.sleep(10 * 60)
            continue

        # 1. 拉取最新备忘录并解包列表
        memos = hola.get('memos', limit=10, order_by='createTime desc').get('memos')

        # 2. 遍历所有备忘录，让AI选择是否回应，并发送评论
        flag = 0
        for memo in memos:
            memo_id = memo['name']

            # 如果备忘录在黑名单中，跳过
            if memo_id in blacklist:
                print(f"跳过黑名单备忘录: {memo_id}")
                continue

            # 避免评论自己的备忘录
            content = hola.get_name_by_id(memo["creator"]) + ": " + memo['content']

            
            # 准备给AI其他人的评论
            comments = hola.get_pretty_comments(memo_id)
            input_prompt = f"{cfg.role_prompt}\n请决定是否回应（建议简短100字，最多250字），如果不想回应，或发现自己评论得太多了（你是{cfg.role_name}），仅回应'ABORT'，或永远不打算回应的'BLACK'（慎用！但是对于无意义内容，尽快使用），否则，直接输出回应内容：\n{content}\n\n其他评论:\n{comments}"

            print(f"处理备忘录: {memo_id}")
            print(f"提示语: {input_prompt}")
            # AI决定是否回应
            response = wrapper.chat(input_prompt, temperature=cfg.role_temperature)
            print(f"AI回应: {response}")
            if "ABORT" in response:
                continue
            elif "BLACK" in response:
                blacklist[memo_id] = time.time() + random.randint(cfg.role_min_wait_time * 240, cfg.role_max_wait_time * 240)  # 黑名单1分钟到1小时
            else:
                hola.create_comment(
                    memo_id,
                    content=response,
                    visibility='PROTECTED',
                )
            flag += 1
            

        # 3. 随机等待一段时间，避免过于频繁
        wait_time = random.randint(cfg.role_min_wait_time * 60, cfg.role_max_wait_time * 60)
        print(f"等待 {wait_time} 秒后继续...")
        time.sleep(wait_time)

        # 4. 检查黑名单中的备忘录是否可以复活
        current_time = time.time()
        for memo_id in list(blacklist.keys()):
            if current_time >= blacklist[memo_id]:
                print(f"备忘录 {memo_id} 已复活，移除黑名单。")
                del blacklist[memo_id]
        
        # 5. 让AI自己写一写备忘录
        if flag < 5 or random.random() < 0.5:
            print("AI写备忘录...")
            ai_memo_content = wrapper.chat(f"{cfg.role_prompt}\n请写一篇新的备忘录，内容可以是任何你想说的。不要有“备忘录”等提示语、标题、署名。", temperature=cfg.role_temperature)
            hola.create_memo(
                content=ai_memo_content,
                visibility='PROTECTED',
            )
            print("AI已创建新备忘录。")

# 脚本入口
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MemosPlus")
    parser.add_argument('--compose', '-c', dest='compose_file', default='compose.yml', help='Path to compose YAML file')
    args = parser.parse_args()
    main(args)

