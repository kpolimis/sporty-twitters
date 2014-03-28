# Sporty Twitters

## Abstract

<!-- The 
correlation between well-being and exercising users

- use of twitter to get a big amount of data
- use of sport tracker apps to get users that exercise
- extension of poms to "compute" the well-being of users

- create a classifier able to detect users that exercise
 -->
## Installation
<!-- 
written in python using packages X,Y, etc

which package do I have to install? (links, short description) -->

## Usage

Each folder in the `src` folder is dedicated to one function. To use the scripts, open a terminal and go to the `src` folder, then use the following command: `python -m folder.script params [options]`

- `clean_corpus` furnishes a script to remove stopwords, mentions, URLs, and punctuation from a given corpus. The default behaviour is to remove everything but flags exist to keep some properties. Moreover, if no stopwords file is given, then no words are removed.

	`python -m clean_corpus.clean_corpus [stopwords_file,--keep-mentions,--keep-urls,--keep-punctuation] < corpus > cleaned_corpus`

- `context_similar` contains three scripts which goal is to find words that have a similar context (i.e. similar neighbourhood) to a given set of words.
	- `build_contexts` takes a corpus file as an input and outputs the contexts in a JSON format.

		`python -m context_similar.build_contexts < corpus > contexts.json`

	- `extend_poms` take the contexts and the POMS words as inputs and outputs the `n` most similar words for each POMS category. It is also possible to restrict the computed POMS categories to a subset using optional parameters.

		`python -m context_similar.extend_poms poms_file poms_legend_file [n, categories] < contexts.json > similarWords`

	- `similarity_scores` contains the implemented methods to compute similarity scores between two words given their contexts:
		- cosineSimilarity

- `poms` 
- `tweet_collect`
- `utils`
- `wordnet`