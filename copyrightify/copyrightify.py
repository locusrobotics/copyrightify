# Software License Agreement (proprietary)
#
# \file      copyrightify.py
# \authors   Paul Bovbel <pbovbel@locusrobotics.com>
# \copyright Copyright (c) (2017,), Locus Robotics, All rights reserved.
#
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.
from __future__ import print_function

import argparse
import datetime
import git
import jinja2
import os
import re
import shutil
import sys
import tempfile
import yaml

from pkg_resources import resource_string

LICENSE_EXTENSION = '.txt'
COPYRIGHT_SCAN_LINES = 20  # Only scan this many lines of a file to check if it has a copyright
SHEBANG_REGEX = re.compile("(^#!/.*)|(^\<\?xml.*)")  # Detect shebangs and xml prolog


def get_context():
    """Read in templating context from various sources.
    """
    context = {}
    git_config = git.GitConfigParser([os.path.normpath(os.path.expanduser("~/.gitconfig"))], read_only=True)
    git_config.read()

    def get_user_config(key):
        try:
            return git_config.get_value('user', key)
        except:
            raise RuntimeError("Please run `git config --global user.{0} '<{0}>'``".format(key))

    for entry in ['name', 'email', 'company']:
        context[entry] = get_user_config(entry)
    context['year'] = datetime.datetime.now().year,

    return context


def find_shebang(line, filetypes):
    """Search line for a shebang, and attempt to extract file type.
    """
    shebang = None
    filetype = None
    if SHEBANG_REGEX.match(line):
        shebang = line
        filetypes = list(filetypes.keys())
        filetypes.sort(key=len, reverse=True)
        for extension in filetypes:
            # This is a little hacky, but should detect any interpreters we currently use (python, bash). May break.
            if extension in shebang:
                filetype = extension
                break

    return shebang, filetype


def process_file(path, config, context):
    """Determine file type (whether via shebang or file extension), and apply header if necessary.
    """
    filetypes = config['filetypes']
    preamble = config['preamble']
    license_text = config['licenses'][context['license']]

    with open(path) as f:
        try:
            shebang_candidate = f.readline()
        except UnicodeDecodeError:
            # Not a unicode text file, skipping
            return

        shebang, filetype = find_shebang(shebang_candidate, filetypes)
        f.seek(0)

        if not filetype:  # Only use file extension if shebang didn't help
            filetype = os.path.splitext(path)[1].lstrip('.')

        try:
            comment_start, line_prefix, comment_end = filetypes[filetype]
        except KeyError:
            print("Extension is unsupported, skipping {}".format(path))
            return

        template = str()

        if comment_start:
            template += comment_start + '\n'

        for line in (preamble + '\n' + license_text).splitlines():
            template += (line_prefix + line).rstrip(' ') + '\n'

        template += comment_end

        header = jinja2.Environment().from_string(template).render(
            filename=os.path.split(path)[1],
            **context)

        # Make a temporary file that will replace the original source
        with tempfile.NamedTemporaryFile(mode='w') as tmp:
            if shebang:
                tmp.write(shebang)  # Make sure shebang is preserved as first line

            print(header, file=tmp)

            for idx, line in enumerate(f):
                if idx == 0 and shebang:
                    continue  # skip copying shebang if we detected one earlier

                if idx < COPYRIGHT_SCAN_LINES and 'Copyright' in line:
                    print("Contains copyright already, skipping {}".format(path))
                    return
                tmp.write(line)

            tmp.flush()
            try:
                shutil.copyfile(tmp.name, path)
                print("Added copyright to {}".format(path))
            except:
                print("Could not overwrite with changes, skipping {}".format(path), file=sys.stderr)


def process_paths(paths, recursive, config, context):
    """Process the target path, which could be a file or a directory. If a directory, we may also
    want to recurse over all subdirectories.
    """
    for path in paths:
        if os.path.isfile(path):
            process_file(path, config, context)
        elif os.path.isdir(path):
            if recursive:
                for subdir, _, files in os.walk(path):
                    for f in files:
                        process_file(os.path.join(subdir, f), config, context)
            else:
                for f in os.listdir(path):
                    file_path = os.path.join(path, f)
                    if os.path.isfile(file_path):
                        process_file(file_path, config, context)
        else:
            print("Not a valid path, skipping {}".format(path), file=sys.stderr)


def main():
    try:
        config = yaml.load(resource_string(__name__, 'config.yaml'))

        parser = argparse.ArgumentParser()
        parser.add_argument('paths', type=str, nargs='+', help='Path to process')
        parser.add_argument('--recursive', '-r', action='store_true', help="Recurse through all subdirectories.")
        parser.add_argument(
            '--license', type=str, default="proprietary", choices=config['licenses'].keys(), help="License type.")
        args, unknown = parser.parse_known_args()

        context = get_context()
        context['license'] = args.license

        process_paths(args.paths, args.recursive, config, context)
        sys.exit(0)
    except Exception as e:
        print("Error: {}".format(e, file=sys.stderr))
        sys.exit(1)


if __name__ == '__main__':
    main()
