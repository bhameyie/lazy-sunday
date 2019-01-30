import os
import platform
import shutil
import subprocess
from dataclasses import dataclass

from flask import current_app

from moviefriday import utils


@dataclass
class ConversionRequirement:
    filename: str
    filepath: str
    cleanup: bool
    hls_start_number: int
    hls_time: int
    hls_list_size: int


def make_default_req(filename, filepath):
    return ConversionRequirement(filename, filepath, cleanup=True, hls_start_number=0, hls_list_size=0, hls_time=10)


def convert_mp4(requirement: ConversionRequirement, force_replace=False):
    ffmpeg = _get_ffmpeg()

    new_folder = os.path.join(os.getcwd(), current_app.config['HLS_DIR'], requirement.filename)

    if os.path.isdir(new_folder):
        if force_replace:
            shutil.rmtree(new_folder)
        else:
            return {"succeeded": False, "reason": "Folder already exists."}

    os.mkdir(new_folder)

    result = _run_ffmpeg(ffmpeg, new_folder, requirement)

    if result["succeeded"] and requirement.cleanup:
        os.remove(requirement.filepath)

    return result


def _get_ffmpeg():
    platform_name = platform.system().lower()
    if platform_name == 'darwin':
        return os.path.join(os.getcwd(), current_app.config['TOOLS_DIR'], 'ffmpeg.osx')

    if platform_name == 'windows':
        arch = platform.architecture()
        if arch[0].lower() == '32bit':
            return os.path.join(os.getcwd(), current_app.config['TOOLS_DIR'], 'ffmpeg.win32.exe')
        return os.path.join(os.getcwd(), current_app.config['TOOLS_DIR'], 'ffmpeg.win64.exe')

    return "ffmpeg"


def _run_ffmpeg(ffmpeg, new_folder, requirement):
    argu = '-i {0} -codec: copy -start_number {1} -hls_time {2} -hls_list_size {3} -f hls {4}.m3u8'.format(
        requirement.filepath, requirement.hls_start_number, requirement.hls_time,
        requirement.hls_list_size, requirement.filename).split(' ')
    with utils.chdir(new_folder):
        ran = subprocess.run([ffmpeg] + argu)
        return {"suceeded": ran.returncode == 0, "reason": ran.stderr}
