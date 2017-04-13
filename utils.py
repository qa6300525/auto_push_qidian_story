import os


def get_file_path(file):
    path = os.path.dirname(os.path.realpath(__file__))
    return path
