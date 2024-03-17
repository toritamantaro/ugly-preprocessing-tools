import functools
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation

from util.text_tool_base import make_pipeline

if __name__ == "__main__":
    '''
    > python -m cleaner.baseline_splitter
    '''

    from util.versatile_tool import stop_watch

    # texts = [
    #     'My name is Jonas E. Smith. Please turn to p. 55.',
    # ]

    texts = [
        'Clinical Stanford Emergency Medicine Dept 300 Pasteur Dr Rm M121 https://colab.research.google.com/drive/13nedT0tB3YJV-d5FPdTCjgW49 Alway Bldg MC 5119 Stanford, CA 94305 (650) 725-4492 (office) (650) 736-7605 (fax) Clinical Stanford Emergency Department 900 Welch Rd Ste 350 Stanford, CA 94305 (650) 725-4492 (office) (650) 736-7605 (fax) Additional Info. Stanford Medicine Antibiograms Your Librarian. Every healthcare provider responding to a disaster should have foundational knowledge of disaster medicine. Log in with your SUNet ID. View All Information for Patients & Visitors », Marc and Laura Andreessen Adult Emergency Department. [https://colab.research.google.com/drive/13nedT0tB3YJV-d5FPdTCjgW49y]'
    ]

    # texts = texts * 1_000  # 0.233517sec
    # texts = texts * 3

    split_punc = functools.partial(split_punctuation, punctuations=r".!?")
    concat_tail_te = functools.partial(concatenate_matching, remove_former_matched=False)

    splitter = make_pipeline(
        normalize,
        split_newline,
        concat_tail_te,
        split_punc,
    )


    @stop_watch
    def func():
        for text in texts:
            print(list(splitter(text)))
            # list(splitter(text))


    func()
