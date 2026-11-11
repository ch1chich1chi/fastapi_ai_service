import json
import os
from pathlib import Path


def load_config(config_path: str = "config.json") -> dict[str, object]:
    path = Path(config_path)

    with path.open("r", encoding="utf-8") as file:
        config: dict[str, object] = json.load(file)

    env_model = os.getenv("AI_MODEL")
    if env_model:
        config["model"] = env_model

    if not config.get("model"): # config.get("model"):读取 model,不存在时返回None
        raise ValueError("缺少必需配置:model") # raise:主动产生错误
        # ValueError:数据内容不符合要求
     
    return config


if __name__ == "__main__":
    result = load_config()
    print(result)
    print(type(result))
    print(type(result["features"]))