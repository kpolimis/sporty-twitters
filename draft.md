one line in the feature matrix: features for one tweet

stemming?
weighting of features? tf, tf-idf
features filtering: top infogain words
evaluation: F1

possible features:

- tweet features:
	- unigrams
	- length of the tweet (small, medium, long)
	- use hashtags (yes/no)
	- is a retweet (yes/no)
	- mentions users (yes/no)
- user features:
	- # favorites
	- # followers
	- # followees
	- why not try and use the avg luminosity of the profile colors
