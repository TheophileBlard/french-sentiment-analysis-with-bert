# French sentiment analysis with BERT
> **How good is BERT ?** Comparing BERT to other SOTA approaches on a **French sentiment analysis** dataset :books:

The contribution of this repository is threefold.

- Firstly, I introduce a new dataset for sentiment analysis, scraped from [Allociné.fr](http://www.allocine.fr/) user reviews.
At my knowledge, there is no dataset of this size in French available on the internet.

- Secondly, I share my code for French sentiment analysis with BERT, based on [CamemBERT](https://camembert-model.fr/).

- Lastly, I compare BERT results with other SOTA approaches, such as TF-IDF and fastText.

## Installation

Linux:

```sh
git clone https://github.com/TheophileBlard/french-sentiment-analysis-with-bert/
cd french-sentiment-analysis-with-bert
pipenv install

cd allocine_dataset
tar xvjf data.tar.bz2
```
## Results


| Model                                        | Validation Accuracy | Validation F1-Score | Test Accuracy | Test F1-Score |
| :--------------------------------------------|--------------------:| -------------------:| -------------:|--------------:| 
| [TF-IDF + logistic regression][tf-idf.ipynb] |                0.92 |                0.92 |      **0.92** |      **0.92** |


## Release History

* 0.0.1
    * Work in progress

## Author

Théophile Blard – :email: theophile.blard@gmail.com

If you use this work (code or dataset), please cite as:

> Théophile Blard, French sentiment analysis with BERT, (2020), GitHub repository, https://github.com/TheophileBlard/french-sentiment-analysis-with-bert

<!-- Markdown link & img dfn's -->
[tf-idf.ipynb]: https://github.com/TheophileBlard/french-sentiment-analysis-with-bert/blob/master/tf-idf.ipynb

