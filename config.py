import yaml

class Config:
    def __init__(self, compose_file):
        self.compose_file = compose_file
        self.load_compose()

    def load_compose(self):
        with open(self.compose_file, 'r', encoding='utf-8') as file:
            self.compose = yaml.safe_load(file)

        self.config_file = self.compose.get("config_file")

        self.load_config()


        self.ai_model = self.compose.get("model", self.config.get("model"))
        if not self.ai_model:
            raise ValueError("AI model not specified in compose file or config file.")
        
        # For Role
        self.role_name = None
        self.role_id = self.compose.get("id") # Like "users/5"
        if self.role_id is None:
            raise ValueError("Role ID not specified in compose file.")
        self.role_prompt = self.compose.get("system_prompt", "我是一个AI助手。我绝对不会返回提示语，而是直接返回结果。")
        self.role_temperature = self.compose.get("temperature", 0.3)
        self.role_min_wait_time = self.compose.get("min_wait_time", 10)
        self.role_max_wait_time = self.compose.get("max_wait_time", 60)
        self.role_morning = self.compose.get("morning", 8)
        self.role_active_hours = self.compose.get("active_hours", 10)

        del self.compose, self.config, self.config_file, self.compose_file


    def load_config(self):
        with open(self.config_file, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)

        # General

        # For AI
        ai = self.config["ai"]
        self.ai_api_key = ai.get("api_key")
        self.ai_base = ai.get("endpoint")

        # For Memos
        memos = self.config["memos"]
        self.memos_base = memos.get("endpoint")
        self.memos_api_key = memos.get("api_key")
        self.memos_insecure = memos.get("insecure", False)

        self.user_list = {}