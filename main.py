import config
from csgo_ranks import csgoRankParser
from loader import LoaderFromFiles

if __name__ == '__main__':
    loader = LoaderFromFiles(config.path_to_account_data, config.path_to_mafiles)
    parser = csgoRankParser(loader.result, config.is_print_console)

    if config.path_to_output != "":
        parser.save_to_file(config.path_to_output)

    if config.is_save_to_buffer:
        parser.save_to_buffer()

    if config.is_print_console:
        parser.result
