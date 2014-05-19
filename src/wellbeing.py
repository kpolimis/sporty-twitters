import expand_vocabulary

class WellBeing():
    """
    Programming Interface dedicated to the development of the well being study
    in the sporty twitters project.
    """

    def __init__(self, expandVocabulary=expand_vocabulary.ContextSimilar):
        self.expandVocabulary = expandVocabulary