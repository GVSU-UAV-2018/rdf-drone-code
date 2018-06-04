from configparser import ConfigParser

def get_config():
    parser = ConfigParser()
    with open('settings.ini', 'r') as config_file:
        parser.read_file(config_file)

    return {
        section_name:{k:eval(v) for k,v in section.items()}
            for (section_name, section) in parser.items()}
