from configparser import ConfigParser

def get_config():
    cfg = ConfigParser()
    cfg.read('./config.ini', encoding="utf-8")
    print(cfg.sections())
    return cfg

if __name__ == '__main__':
    cfg = get_config()
    print(cfg.sections())
    print(cfg["init_meanabs"]['super_msg'])