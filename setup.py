from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

config = dict(name='CloudHarvestCorePluginManager',
              version='0.1.0',
              description='This module is responsible for managing plugins and their configurations.'
                          ' It is designed to work with both the Cloud Harvest API and the Cloud Harvest CLI to load'
                          ' components from plugins such as the Cloud Harvest AWS Plugin.',
              author='Cloud Harvest, Fiona June Leathers',
              url='https://github.com/Cloud-Harvest/CloudHarvestCorePluginManager',
              packages=find_packages(include=['CloudHarvestCorePluginManager']),
              install_requires=required,
              classifiers=[
                  'Programming Language :: Python :: 3.12',
              ],
              license='CC Attribution-NonCommercial-ShareAlike 4.0 International')


def main():
    setup(**config)


if __name__ == '__main__':
    main()
