"""Generates a list of CFGs from a path.

The module finds all python modules and generates an ast for them.
"""
import os


_local_modules = list()


def get_directory_modules(directory):
    """This function returns a list of tuples containing the names and paths of the modules in a given directory. It first checks if the list of local modules is already populated and if the directory matches the directory of the first module in the list. If so, it returns the list as is. If not, it checks if the given directory is a valid directory. If it is not, it sets the directory to the parent directory of the given file path. Then, it iterates through the files in the directory and checks if each file is a Python file. If it is, it extracts the module name by removing the file extension and adds a tuple of the module name and the file path to the list of local modules. Finally, it returns the list of local modules.
    Input-Output Arguments
    :param directory: String. The directory to search for modules.
    :return: List of tuples. A list containing tuples of module names and file paths.
    """


def get_modules(path, prepend_module_root=True):
    """Return a list containing tuples of
    e.g. ('test_project.utils', 'example/test_project/utils.py')
    """
    module_root = os.path.split(path)[1]
    modules = list()
    for root, directories, filenames in os.walk(path):
        for filename in filenames:
            if _is_python_file(filename):
                directory = os.path.dirname(
                    os.path.realpath(
                        os.path.join(
                            root,
                            filename
                        )
                    )
                ).split(module_root)[-1].replace(
                    os.sep,  # e.g. '/'
                    '.'
                )
                directory = directory.replace('.', '', 1)

                module_name_parts = []
                if prepend_module_root:
                    module_name_parts.append(module_root)
                if directory:
                    module_name_parts.append(directory)

                if filename == '__init__.py':
                    path = root
                else:
                    module_name_parts.append(os.path.splitext(filename)[0])
                    path = os.path.join(root, filename)

                modules.append(('.'.join(module_name_parts), path))

    return modules


def _is_python_file(path):
    if os.path.splitext(path)[1] == '.py':
        return True
    return False