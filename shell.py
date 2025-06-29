from config import Config

import rich
import code
import requests
import importlib
import hola as _hola_mod
import wrapper as _wrapper_mod

cfg = Config("compose.yml")
hola = _hola_mod.Hola(cfg)
wrapper = _wrapper_mod.ModelWrapper(cfg)

def restart():
    """
    重新加载 hola.py 和 wrapper.py，并重新创建 hola、wrapper 实例
    """
    global _hola_mod, _wrapper_mod, hola, wrapper
    _hola_mod = importlib.reload(_hola_mod)
    _wrapper_mod = importlib.reload(_wrapper_mod)
    hola = _hola_mod.Hola(cfg)
    wrapper = _wrapper_mod.ModelWrapper(cfg)
    local_vars.update({'hola': hola, 'wrapper': wrapper})
    print("Shell restarted: modules reloaded and instances recreated.")

# 创建本地变量环境
local_vars = {
    'hola': hola,
    'wrapper': wrapper,
    'cfg': cfg,
    'rich': rich,
    'requests': requests, 
    'rs': restart, 
    'print': rich.print,
}

print("Memos Interactive Shell")
print("Available variables: hola, wrapper, cfg, rich, requests")

# 启动交互式解释器
console = code.InteractiveConsole(locals=local_vars)
console.interact()