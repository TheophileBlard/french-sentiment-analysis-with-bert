# French sentiment analysis with BERT

> **How good is BERT ?** Comparing BERT to other state-of-the-art approaches on a large-scale **French sentiment analysis** dataset :books:

The contribution of this repository is threefold.

- Firstly, I introduce a new dataset for sentiment analysis, scraped from [Allociné.fr](http://www.allocine.fr/) user reviews.
It contains 100k positive and 100k negative reviews divided into 3 balanced splits: train (160k reviews), val (20k) and test (20k).
At my knowledge, there is no dataset of this size in French language available on the internet.

- Secondly, I share my code for French sentiment analysis with BERT, based on [CamemBERT](https://camembert-model.fr/), and the [🤗Transformers](https://github.com/huggingface/transformers) library.

- Lastly, I compare BERT results with other state-of-the-art approaches, such as *TF-IDF* and *fastText*, as well as other non-contextual word embeddings based methods.

## Installation

If you want to experiment with the training code, follow these steps:

```sh
# Download repo and its dependencies 
git clone https://github.com/TheophileBlard/french-sentiment-analysis-with-bert/
cd french-sentiment-analysis-with-bert
pipenv install

# Extract dataset
cd allocine_dataset && tar xvjf data.tar.bz2 && cd ..

# Activate virtualenv and open-up BERT notebook
pipenv shell
jupyter notebook 03_bert.ipynb 
```

But if you only need the model for inference, please refer to [this paragraph](#hugging-face-integration).

## Dataset

The dataset is made available as [`.jsonl`](http://jsonlines.org/) files, as well as a [`.pickle`](https://docs.python.org/3/library/pickle.html) file.
Some examples from the training set are presented in the following table:

| Review                                                                              |  Polarity  |
| :---------------------------------------------                                      |----------|
| *Magnifique épopée, une belle histoire, touchante avec des acteurs qui interprètent très bien leur rôles (Mel Gibson, Heath Ledger, Jason Isaacs...), le genre de film qui se savoure en famille!*                                                   |  Positive  |
| *N'étant pas fan de SF, j'ai du mal à commenter ce film. Au moins, dirons nous, il n'y a pas d'effets spéciaux et le thème de ces 3 derniers survivants, un blanc, un maori, une blanche est assez bien traité. Mais c'est quand même bien longuet* !        |  Negative  |
| *Les scènes s'enchaînent de manière saccadée, les dialogues sont théâtraux, le jeu des acteurs ne transcende pas franchement le film. Seule la musique de Vivaldi sauve le tout. Belle déception.*                                                   |  Negative  |

For more information, please refer to the [dedicated page][allocine-readme].

The dataset is also available in the [🤗Datasets library](https://huggingface.co/datasets), please refer to [this paragraph](#hugging-face-integration).

## Results

### Full dataset

| Model                                        | Validation Accuracy | Validation F1-Score | Test Accuracy | Test F1-Score |
| :--------------------------------------------|--------------------:| -------------------:| -------------:|--------------:|
| **[CamemBERT][bert.ipynb]**                  |           **97.39** |           **97.36** |     **97.44** |     **97.34** |
| [RNN][word-vectors.ipynb]                    |               94.39 |               94.34 |         94.58 |         94.39 |
| [TF-IDF + LogReg][tf-idf.ipynb]              |               94.35 |               94.29 |         94.38 |         94.19 |
| [CNN][word-vectors.ipynb]                    |               93.69 |               93.72 |         94.10 |         93.98 |
| [fastText (unigrams)][word-vectors.ipynb]    |               92.88 |               92.75 |         92.90 |         92.57 |

> CamemBERT outperforms all other models by a large margin.

### Learning curves

Test accuracy as a function of training dataset size.

<p align="center">
    <img src="/img/learning_curves.png" width="750" >
</p>

> With only 500 training examples, CamemBERT is already showing better results that any other model trained on the full dataset.
> This is the power of modern language models and self-supervised pre-training.

> For this kind of tasks, RNNs need a lot of data (>100k) to perform well.
> The same result (for English language) is empirically observed by Alec Radford in [these slides](https://docs.google.com/presentation/d/102TFe5dAmUXja_Ft31z__NUUuY7PZG9AkV7Qn_TwPXg/edit#slide=id.g58433b516_80).

### Inference time

Time taken by a model to perform a single prediction (averaged on 1000 predictions).

<p align="center">
    <img src="/img/inference_time.png" width="550" >
</p>

> As one would expect, the slowest model is *CamemBERT*, followed by *TF-IDF*.

> On the other hand, *fastText* performs the ... fastest, but is actually slow compared to the [original implementation](https://github.com/facebookresearch/fastText), because of the overhead of Python and Keras.

### Generalizability

I considered the text classification task from [FLUE](https://github.com/getalp/Flaubert/tree/master/flue) (French Language Understanding Evaluation) to evaluate the cross-domain generalization capabilities of the models. This is also a binary classification task, but on [Amazon](https://www.amazon.fr/) product reviews.

There is one train and test set for each product category (*books*, *DVD* and *music*).
The train and test sets are balanced, including around 1000 positive and 1000 negative reviews, for a total of 2000 reviews in each dataset.

I didn't do any additional training, only inference on the test sets.
The resulting accuracies are reported in the following table:

| Model                                        | Books               | DVD                 |         Music |
| :--------------------------------------------|:-------------------:|:-------------------:|:-------------:|
| **[CamemBERT][bert.ipynb]**                  |           **94.10** |           **93.25** |     **94.55** |
| [TF-IDF + LogReg][tf-idf.ipynb]              |               87.10 |               88.10 |         87.45 |
| [CNN][word-vectors.ipynb]                    |               85.80 |               88.75 |         87.25 |
| [RNN][word-vectors.ipynb]                    |               85.30 |               87.55 |         87.50 |
| [fastText (unigrams)][word-vectors.ipynb]    |               85.25 |               87.10 |         86.65 |

> Without additional training on domain-specific data, the *CamemBERT* model outperforms finetuned *CamemBERT* & *FlauBERT* models reported in [(He et al., 2020)](https://arxiv.org/abs/1912.05372). **Update:** FlauBERT (Large) released 03/20 gets better results, but it is excessively heavy. 

> *TF-IDF + LogReg* also performs better than specifically-trained *mBERT* [(Eisenschlos et al., 2019)](https://arxiv.org/abs/1909.04761).

## Hugging Face Integration

The CamemBERT model is now [part of the 🤗Transformers library](https://huggingface.co/tblard/tf-allocine) !
You can retrieve it and perform inference with the following code:

```python
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import pipeline

tokenizer = AutoTokenizer.from_pretrained("tblard/tf-allocine")
model = TFAutoModelForSequenceClassification.from_pretrained("tblard/tf-allocine")

nlp = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

print(nlp("Alad'2 est clairement le meilleur film de l'année 2018.")) # POSITIVE
print(nlp("Juste whoaaahouuu !")) # POSITIVE
print(nlp("NUL...A...CHIER ! FIN DE TRANSMISSION.")) # NEGATIVE
print(nlp("Je m'attendais à mieux de la part de Franck Dubosc !")) # NEGATIVE
```
The dataset is also [available in 🤗Datasets](https://huggingface.co/datasets/viewer/?dataset=allocine). 
To download it and start training your own model, simply use:

```python
import datasets

train_ds, val_ds, test_ds = datasets.load_dataset(
    'allocine', 
    split=['train', 'validation', 'test']
)
```

## Online Demo

Open the online demo on Google Colab: 

<p>
<p align="center">
    <a href="https://colab.research.google.com/github/TheophileBlard/french-sentiment-analysis-with-bert/blob/master/colab/french_sentiment_analysis_with_bert.ipynb">
        <img alt="Colab Demo" src="https://colab.research.google.com/assets/colab-badge.svg">
    </a>    
</p>

## Release History

- 0.4.0
  - Uploaded model to <https://huggingface.co/tblard/tf-allocine>
  - Uploaded the dataset to <https://huggingface.co/datasets/viewer/?dataset=allocine>
- 0.3.0
  - Added Google Colab online demo
- 0.2.0
  - Added inference time + generalizability
- 0.1.0
  - First proper release
  - Learning curves & results for all models
- 0.0.1
  - Work in progress

## Task List

- [x] *Dataset available*
- [x] *Models available*
- [x] *Results on full dataset*
- [x] *Learning curves*
- [x] *Inference time*
- [x] *Generalizability*
- [x] *Online demo*
- [x] *Hugging Face integration*
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
