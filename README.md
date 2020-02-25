# French sentiment analysis with BERT

> **How good is BERT ?** Comparing BERT to other SOTA approaches on a large-scale **French sentiment analysis** dataset :books:

The contribution of this repository is threefold.

- Firstly, I introduce a new dataset for sentiment analysis, scraped from [Allociné.fr](http://www.allocine.fr/) user reviews.
It contains 100k positive and 100k negative reviews divided into 3 balanced splits: train (160k reviews), val (20k) and test (20k).
At my knowledge, there is no dataset of this size in French language available on the internet.

- Secondly, I share my code for French sentiment analysis with BERT, based on [CamemBERT](https://camembert-model.fr/), and the [🤗Transformers](https://github.com/huggingface/transformers) library.

- Lastly, I compare BERT results with other SOTA approaches, such as *TF-IDF* and *fastText*, as well as other non-contextual word embeddings based methods.

## Installation

Linux:

```sh
git clone https://github.com/TheophileBlard/french-sentiment-analysis-with-bert/
cd french-sentiment-analysis-with-bert
pipenv install

cd allocine_dataset
tar xvjf data.tar.bz2
```

## Dataset

The dataset is made available as [`.jsonl`](http://jsonlines.org/) files, as well as a [`.pickle`](https://docs.python.org/3/library/pickle.html) file.
Some examples from the training set are presented in the following table.

| Review                                                                              |  Polarity  |
| :---------------------------------------------                                      |----------|
| *Magnifique épopée, une belle histoire, touchante avec des acteurs qui interprètent très bien leur rôles (Mel Gibson, Heath Ledger, Jason Isaacs...), le genre de film qui se savoure en famille!*                                                   |  Positive  |
| *N'étant pas fan de SF, j'ai du mal à commenter ce film. Au moins, dirons nous, il n'y a pas d'effets spéciaux et le thème de ces 3 derniers survivants, un blanc, un maori, une blanche est assez bien traité. Mais c'est quand même bien longuet* !        |  Negative  |
| *Les scènes s'enchaînent de manière saccadée, les dialogues sont théâtraux, le jeu des acteurs ne transcende pas franchement le film. Seule la musique de Vivaldi sauve le tout. Belle déception.*                                                   |  Negative  |

For more information, please refer to the [dedicated page][allocine-readme].

## Results

### Full dataset

| Model                                        | Validation Accuracy | Validation F1-Score | Test Accuracy | Test F1-Score |
| :--------------------------------------------|--------------------:| -------------------:| -------------:|--------------:|
| **[CamemBERT][bert.ipynb]**                  |           **97.39** |           **97.36** |     **97.44** |     **97.34** |
| [RNN][word-vectors.ipynb]                    |               94.39 |               94.34 |         94.58 |         94.39 |
| [TF-IDF + LogReg][tf-idf.ipynb]              |               94.35 |               94.29 |         94.38 |         94.19 |
| [CNN][word-vectors.ipynb]                    |               93.69 |               93.72 |         94.10 |         93.98 |
| [fastText (unigrams)][word-vectors.ipynb]    |               92.88 |               92.75 |         92.90 |         92.57 |

### Learning curves

Test accuracy as a function of training dataset size.

<p align="center">
    <img src="/img/learning_curves.png" width="750" >
</p>

### Inference time

Time taken by a model to perform a single prediction (averaged on 1000 predictions).

<p align="center">
    <img src="/img/inference_time.png" width="750" >
</p>

## Release History

- 0.1.0
  - The first proper release
  - Learning curves & results for all models
- 0.0.1
  - Work in progress

## Task List

- [x] *Dataset available*
- [x] *Models available*
- [x] *Results on full dataset*
- [x] *Learning curves*
- [x] *Inference time*
- [ ] *Generalizability*
- [ ] *Online demo*
- [ ] *Predicting usefulness*

## Author

Théophile Blard – :email: theophile.blard@gmail.com

If you use this work (code or dataset), please cite as:

> Théophile Blard, French sentiment analysis with BERT, (2020), GitHub repository, <https://github.com/TheophileBlard/french-sentiment-analysis-with-bert>

<!-- Markdown link & img dfn's -->
[tf-idf.ipynb]: https://github.com/TheophileBlard/french-sentiment-analysis-with-bert/blob/master/01_tf-idf.ipynb
[word-vectors.ipynb]: https://github.com/TheophileBlard/french-sentiment-analysis-with-bert/blob/master/02_word-vectors.ipynb
[bert.ipynb]: https://github.com/TheophileBlard/french-sentiment-analysis-with-bert/blob/master/03_bert.ipynb
[allocine-readme]: https://github.com/TheophileBlard/french-sentiment-analysis-with-bert/blob/master/allocine_dataset/
