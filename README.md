# RTTE
RedditTitleTickerExtracter short RTTE is a small tool that generates a time series database based on the titles and ticker posted in r/wallstreetbets. It collects title, ticker in the title and timestamps when the post was created. It was a try to answer the question if it is possible to find correlation between r/wallstreetbets posts and changes in the stock market inspired by the rise of $GME. To simply answer the the question: It is not possible to find correlation between rising stocks and posts on WSB.

It uses the following packages:
- praw (https://praw.readthedocs.io/en/stable/)
- enchant (https://pypi.org/project/pyenchant/)
- pymongo (https://pymongo.readthedocs.io/en/stable/)
- logging (https://pypi.org/project/pylogging/)
- datetime (https://docs.python.org/3/library/datetime.html)
- cleantext (https://pypi.org/project/clean-text/)

