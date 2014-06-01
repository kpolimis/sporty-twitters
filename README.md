# Sporty Twitters

## Abstract

This project has been realized on a 6 month period (2014/1 - 2014/7) at the Illinois Institute of Technology. It has been supervised by [Dr. Aron Culotta](http://cs.iit.edu/~culotta/).

The goal of this project is to find a correlation between the well-being of a person and the fact that this person regularly exercises.

This project relies on machine learning techniques, it uses the Twitter API to collect data on users, and it depends of sport tracking apps (RunKeeper, Nike+, ...) to detect sportive users.

## Installation

This project is written in Python and uses the following packages:

- [sklearn](http://scikit-learn.org/stable/)
- [nltk](http://www.nltk.org/)
- [TwitterAPI](https://github.com/geduldig/TwitterAPI)
- [docopt](http://docopt.org/)

<!-- TODO: setup.py -->

## Usage

This project has been developed so that other people can re-run the experiment, tweak some parameters, and maybe obtain better results. 

The different parts of the project are centralized in a unique API named `sporty`.