from configparser import ConfigParser

def get_config():
    parser = ConfigParser()
    with open('settings.ini', 'r') as config_file:
        parser.readfp(config_file)

    return {
        section_name:{k:eval(v) for k,v in parser.items(section_name)}
            for section_name in parser.sections()}
