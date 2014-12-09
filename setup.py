try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='Sporty Twitters',
      version='1.0',
      description='Code and data for the AAAI2015 paper entitled "Using matched samples to estimate the effects of exercise on mental health from Twitter", by Virgile Landeiro Dos Reis and Aron Culotta.',
      author='Virgile Landeiro Dos Reis, Aron Culotta',
      author_email='vlandeir@hawk.iit.edu',
      url='https://github.com/tapilab/aaai-2015-matching',
      packages=['sporty', 'cli'],
      package_dir={'sporty': 'src/sporty', 'cli': 'src/cli'},
      py_modules=['sporty.mood',
                  'sporty.sporty',
                  'sporty.tweets',
                  'sporty.user',
                  'sporty.utils'],
      install_requires=[
      					'TwitterAPI',
                        'docopt'
                       ],
      entry_points={'console_scripts': [
                    'sporty-cli = cli.cli:main'
                    ]}
      )
