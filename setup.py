try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='Sporty Twitters',
      version='0.1',
      description='Source code to the sporty twitters project looking to correlate the amount of exercise of a Twitter user with its well-being.',
      author='Virgile Landeiro',
      author_email='vlandeir@hawk.iit.edu',
      url='https://github.com/vlandeiro/sporty-twitters',
      packages=['sporty', 'cli'],
      package_dir={'sporty': 'src/sporty', 'cli': 'src/cli'},
      py_modules=['sporty.mood', 'sporty.sporty', 'sporty.tweets', 'sporty.user', 'sporty.utils'],
      requires=['nltk', 'sklearn', 'TwitterAPI', 'docopt'],
      entry_points={
        'console_scripts': [
            'sporty = cli.cli:main'
        ]}
      )