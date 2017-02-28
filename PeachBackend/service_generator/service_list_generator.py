import os
import argparse
import re

def generate_service_list(directory, ignored_dirs, config_file):
    """
    Generates a list containing paths pointing to the directory containing the latest service found
    @param directory the top level directory
    @param ignored_dirs those directories will be ignored
    @param config_file the name of the configuration file
    @return a list where each entry represents a filepath to a service config
    """
    service_config_paths = []
    for root, dirs, files in os.walk(directory):
        for ignored_dir in ignored_dirs:
            if ignored_dir in dirs:
                dirs.remove(ignored_dir)
        #TODO regex is not bullet proof e.g. 7d will be detected
        regex = re.compile("^v-?[0-9]+$")
        versions = [int(m.group(0).replace("v", "")) for d in dirs for m in [regex.search(d)] if m ]
        if len(versions):
            max_version = max(versions)
            service_config_paths.append(root + os.sep + dirs[versions.index(max_version)] + os.sep + config_file)
    return service_config_paths

def write_out(out_file_path, service_list):
    out_file = open(out_file_path, "w")
    for service in service_list:
        out_file.write("{};".format(service))
    out_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a list containing all services in a directory.')
    parser.add_argument('-d', '--directory', type=str, help="The directory where the search should be started.")
    parser.add_argument('-i', '--ignore', type=str, nargs='+', default="", help="Those directories will be ignored.")
    parser.add_argument('-c', '--config_file', type=str, default = "service.config", help="Specifies the name of the config file, e.g. service.config.")
    parser.add_argument('-u', '--user', type=str, help="The database user.")
    parser.add_argument('-o', '--out_file_path', type=str, default="", help="Filepaths written to a csv file.")
    args = parser.parse_args()
    service_list = generate_service_list(args.directory, args.ignore, args.config_file)
    if args.out_file_path:
        write_out(args.out_file_path, service_list)

