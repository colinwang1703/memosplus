"""
用于和Memos应用交互的类
"""
import requests

requests.packages.urllib3.disable_warnings()  # 禁用SSL警告

class Hola:
    def __init__(self, config):
        self.config = config

    def get(self, name, **params):
        """
        发送GET请求
        """
        response = requests.get(f"{self.config.memos_base}api/v1/{name}", headers={
            'Authorization': f'Bearer {self.config.memos_api_key}'
        }, params=params, verify=not self.config.memos_insecure)
        response.raise_for_status()
        return response.json()     
     
    def post(self, name, data):
        """
        发送POST请求
        """
        response = requests.post(f"{self.config.memos_base}api/v1/{name}", headers={
            'Authorization': f'Bearer {self.config.memos_api_key}',
        }, json=data, verify=not self.config.memos_insecure)
        response.raise_for_status()
        return response.json()
    
    def create_memo(self, content, **kwargs):
        """
        创建一个新的备忘录
        """
        data = {
            "content": content,
            "state": kwargs.get("state", "NORMAL"),
            "visibility": kwargs.get("visibility", "PROTECTED"),
            "pinned": False,
            "resources": [],
            "relations": [],
        }
        return self.post("memos", data)
    
    def create_comment(self, id, content, **kwargs):
        data = {
            "content": content,
            "visibility": kwargs.get("visibility", "PROTECTED"),
        }
        try:
           self.post(f"{id}/comments", data)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print(f"备忘录 {id} 不存在，无法添加评论。")
            else:
                raise e
    
    def _get_comments(self, id, limit=99, order_by='createTime desc'):
        """
        获取指定备忘录的评论
        """
        params = {
            'limit': limit,
            'orderBy': order_by
        }
        return self.get(f"{id}/comments", **params)
    
    def get_pretty_comments(self, id, limit=99, order_by='createTime desc'):
        """
        获取指定备忘录的评论，并格式化输出
        """
        comments = self._get_comments(id, limit, order_by)["memos"]
        return "\n".join([f"{self.get_name_by_id(comment['creator'])}: {comment['content']}" for comment in comments])
    
  
    def whoami(self, id=None):
        """
        获取并更新当前用户信息
        """
        if id is None:
          user_config = self.get(self.config.role_id)
          self.config.role_name = user_config.get('nickname', user_config.get('username'))
          return user_config
        elif id == "for":
          # 遍历
          flag = 1
          configs = []
          while True:
              try:
                user_config = self.get(f"users/{flag}")
                configs.append(user_config)
                flag += 1
              except requests.HTTPError as e:
                if e.response.status_code == 404:
                    break
          return configs
        else:
          return self.get(id)
    
    def second_init(self):
        self.whoami()
        raw = self.whoami("for")
        for user in raw:
          self.config.user_list[user['name']] = user['nickname']
           

    def get_name_by_id(self, id):
        """
        根据用户ID获取用户名
        """
        return self.config.user_list.get(id)