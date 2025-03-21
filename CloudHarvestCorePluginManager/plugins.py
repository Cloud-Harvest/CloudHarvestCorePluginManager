from logging import getLogger
from os.path import abspath, expanduser
from typing import List


logger = getLogger('harvest')
DEFAULT_PLUGIN_FILE = abspath(expanduser('./app/plugins.txt'))


def generate_plugins_file(plugins: List[dict], file_path: str = DEFAULT_PLUGIN_FILE):
    """
    Populates the plugins.txt file with the plugins to install

    Arguments
    plugins (List[dict]) - the plugins to write to the file
    file_path (str, optional) - the file path to write the plugins to
    """

    path = abspath(expanduser(file_path or DEFAULT_PLUGIN_FILE))

    # Make sure the target directory exists
    from pathlib import Path
    from os import sep
    p = Path(sep.join((path).split(sep)[0:-1]))
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as plugins_file:
        for plugin in plugins:

            # Check if the plugin is a git repository or a URL
            from re import compile

            git_pattern = compile(r'^(git\+|)(http|https)://')
            if git_pattern.match(plugin['url_or_package_name']):
                # Get the package name from the URL
                package_name = plugin['url_or_package_name'].split('/')[-1].split('.')[0]

                if 'git+' not in plugin['url_or_package_name']:
                    url = f'git+{plugin["url_or_package_name"]}'

                else:
                    url = plugin["url_or_package_name"]

                branch_name = plugin.get('branch') or 'master'
                output_string = f'{package_name} @ {url}@{branch_name}\n'

            else:
                output_string = plugin['url_or_package_name']

            plugins_file.write(output_string)
            logger.debug(f'Plugin {output_string} written to {path}')


def install_plugins(quiet: bool = False, file_path: str = DEFAULT_PLUGIN_FILE):
    """
    Installs the plugins in the plugins.txt file.

    Arguments
    quiet (bool, optional) - whether to install the plugins quietly
    file_path (str, optional) - the file path to read the plugins from
    """

    path = abspath(expanduser(file_path or DEFAULT_PLUGIN_FILE))

    # Make sure the target file exists
    from os.path import exists
    if not exists(path):
        logger.error(f'Plugins file not found at {path}')
        return

    from subprocess import run
    command = ['pip', 'install', '-r', path]

    if quiet:
        command.append('--quiet')

    execution = run(command)

    if execution.returncode == 0:
        logger.info('Plugins installed successfully')

    else:
        logger.error('Error installing plugins')

    from CloudHarvestCorePluginManager import register_all
    register_all()

def read_plugins_file(file_path: str = DEFAULT_PLUGIN_FILE):
    """
    Reads the plugins.txt file and returns the list of plugins.

    Arguments
    file_path (str, optional) - the file path to read the plugins from
    """

    path = abspath(expanduser(file_path or DEFAULT_PLUGIN_FILE))

    with open(path) as plugins_file:
        plugins = [
            line.strip()
            for line in plugins_file.readlines()
        ]

    result = []

    for plugin in plugins:
        if 'git+' in plugin:
            plugin_split = plugin.split('@')
            url = plugin_split[1].replace('git+', '').strip()

            if len(plugin_split) > 2:
                branch = plugin_split[2].strip()

            else:
                branch = 'main'

            result.append({
                'url_or_package_name': url,
                'branch': branch
            })

        else:
            result.append({
                'url_or_package_name': plugin.replace('\n', '')
            })

    return result
