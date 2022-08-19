import praw, enchant, pymongo, logging
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
    keywords = ["WSB", "YOLO", "BEEP", "BOOP", "HODLL", "HODL"]

    return value in keywords


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(filename='application.log', level=logging.DEBUG)

    reddit = praw.Reddit("bot1")

    # Setup Mongo
    # If collection does not exist it should be created but container has to run (obviously)
    my_client = pymongo.MongoClient("mongodb://localhost:27017/")
    my_db = my_client["test"]
    my_col = my_db["ticker"]

    if reddit.user.me():
        logging.info('=== CONNECTED ===')

    subreddit = reddit.subreddit("wallstreetbets")

    for submission in subreddit.stream.submissions():
        words = submission.title.split()

        gen = (x for x in words if not (not (3 <= len(x) <= 5) or not str.isupper(x) or contains_number(
            x) or not contains_only_valid_special(x)) and not is_a_normal_word(x) and not is_keyword(x))

        for word in gen:
            normalized_word = word.replace("$", "")

            existing = my_col.find_one({"postid": submission.id, "name": normalized_word})

            if not existing:
                insert_dict = dict(postid=submission.id, name=normalized_word,
                                   title=clean(submission.title, no_emoji=True),
                                   timestamp=datetime.fromtimestamp(submission.created))
                result = my_col.insert_one(insert_dict)
                logging.info(insert_dict)

            else:
                logging.info('= DO NOT INSERT ALREADY INSERTED =')