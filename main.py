import os
import config
from csgo_ranks import CSGORankParser
from loader import LoaderFromFiles

if __name__ == '__main__':
    loader = LoaderFromFiles(config.path_to_account_data, config.path_to_mafiles)
    parser = CSGORankParser(loader.result, config.is_print_console)

    if config.is_print_console:
        print("login\t", "level", "exp", "levelUp", "case", "days since last session", sep='\t')
        parser.result

    if config.path_to_output != "":
        parser.save_to_file(config.path_to_output)

    if config.is_save_to_buffer:
        parser.save_to_buffer()

    os.system("pause")
