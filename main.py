import praw, enchant, pymongo, logging
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import yfinance as yf

from datetime import datetime, timedelta
from cleantext import clean


# just some helper functions to filter none ticker related keywords wsb-people use
def contains_number(value):
    for character in value:
        if character.isdigit():
            return True
    return False


def contains_only_valid_special(value):
    for letter in value:
        if not str.isalnum(letter) and not letter == '$':
            return False
    return True


def is_a_normal_word(value):
    d = enchant.Dict("en_US")
    test = d.check(value)
    return test


def is_keyword(value):
    keywords = {"WSB", "YOLO", "BEEP", "BOOP", "HODLL", "HODL", "FOMO"}

    return value in keywords


# noinspection PyBroadException
def find_performance_for_ticker(value):
    try:
        ticker = yf.Ticker(value)

        history = ticker.history(period="1d", start=datetime.today() - timedelta(days=1), end=datetime.today())

        open_price = history['Open'].iloc[0]
        close_price = history['Close'].iloc[0]

        return dict(open=open_price, close=close_price)
    except:
        logging.error(f'Error finding ticker {value}.')
        return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(filename='application.log', level=logging.DEBUG)

    reddit = praw.Reddit("bot1")

    # Setup Mongo
    # If collection does not exist it should be created but container has to run (obviously)
    my_client = pymongo.MongoClient("mongodb://localhost:27017/")
    my_db = my_client["test"]

    ticker_col = my_db["ticker"]
    ticker_performance_col = my_db["ticker_performance"]

    if reddit.user.me():
        logging.info('=== CONNECTED ===')

    subreddit = reddit.subreddit("wallstreetbets")

    for submission in subreddit.stream.submissions():
        words = submission.title.split()
        date = datetime.fromtimestamp(submission.created).strftime('%d/%m/%Y')

        gen = (x for x in words if not (not (3 <= len(x) <= 5) or not str.isupper(x) or contains_number(
            x) or not contains_only_valid_special(x)) and not is_a_normal_word(x) and not is_keyword(x))

        inserted = False

        for word in gen:
            normalized_word = word.replace("$", "")

            existing = ticker_col.find_one({"postid": submission.id, "name": normalized_word})

            if not existing:
                insert_dict = dict(postid=submission.id, name=normalized_word,
                                   title=clean(submission.title, no_emoji=True),
                                   timestamp=date)
                result = ticker_col.insert_one(insert_dict)
                logging.info(insert_dict)

                inserted = True
            else:
                logging.info('= DO NOT INSERT ALREADY INSERTED =')

        if inserted:
            performance_dict = find_performance_for_ticker(normalized_word)

            if performance_dict:
                performance_insert_dict = dict(ticker=normalized_word,
                                   open=performance_dict["open"],
                                   close=performance_dict["close"],
                                   timestamp=date)

                existing = ticker_performance_col.find_one(performance_insert_dict)

                if not existing:
                    result = ticker_performance_col.insert_one(performance_insert_dict)
                    logging.info(performance_insert_dict)

            # Simple visualisation with seaborn - not in use right now
            # plt.close()
            # result = [x for x in ticker_col.find({})]
            # df = pd.DataFrame(result)
            # ax = sns.histplot(x="timestamp", hue="name", data=df, multiple="dodge", shrink=0.1)
            # plt.show()
            # End of visualization
