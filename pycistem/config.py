from pathlib import Path

import appdirs
import yaml

config = {
    "CISTEM_PATH": "/usr/local/bin/"
}
config_path = Path(appdirs.user_config_dir("pycistem","cistem")) / "config.yaml"
if config_path.exists():
    with open(config_path) as fp:
        config_file = yaml.safe_load(fp)
        if "CISTEM_PATH" in config:
            config["CISTEM_PATH"] = config_file["CISTEM_PATH"]

def set_cistem_path(path):
    config["CISTEM_PATH"] = path
    config_path.parent.mkdir(parents=True,exist_ok=True)
    with open(config_path,"w") as fp:
        yaml.dump(config,fp)
