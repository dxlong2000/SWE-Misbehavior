"""Helper Methods to get service definition information out of the boto library"""
import fnmatch
import json
import os

from pkg_resources import resource_filename, Requirement


def boto_service_definition_files():
    """Return paths to all service definition files from botocore"""

    botocore_data_dir = resource_filename(Requirement.parse("botocore"), "botocore/data")
    files = [os.path.join(dirname, file_in_dir)
             for dirname, _, files_in_dir in os.walk(botocore_data_dir)
             for file_in_dir in files_in_dir
             if fnmatch.fnmatch(file_in_dir, 'service-*.json')]
    return files


def service_definition_file(servicename):
    """This function returns the path to the most recent service definition file for a given service. It first retrieves all the service definition files. Then, it filters the files based on the provided service name and a specific pattern ("**/" + servicename + "/*/service-*.json"). The filtered files are sorted in ascending order based on their names, and the path of the last file is returned.
    Input-Output Arguments
    :param servicename: String. The name of the service.
    :return: String. The path to the most recent service definition file for the given service.
    """


def operation_definition(servicename, operationname):
    """Returns the operation definition for a specific service and operation"""
    with open(service_definition_file(servicename), encoding="UTF-8") as definition_file:
        service_definition = json.loads(definition_file.read())
        return service_definition['operations'][operationname]