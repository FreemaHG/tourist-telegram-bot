## Getting started
This bot is tested with Python 3.9 and pyTelegramBotAPI 4.4.0.

* Downloading files from the repository
```
$ git clone https://gitlab.skillbox.ru/dmitrii_stafeev/python_basic_diploma.git
```
* Installing dependencies
```
$ pip install -r requirements.txt
```
## Commands
* ### /start
Output of a simple welcome message
* ### /help
Output of a hint message with a list of supported commands and a brief description of each of them.
* ### /lowprice
Conclusion of the TOP cheap hotels in the selected location.
* ### /highprice
Output of the TOP expensive hotels in the selected location.
* ### /bestdeal
Conclusion of the TOP offers for hotels in the selected location according to the ratio of price and distance to the 
city center (price is a priority).
* ### /history
Output of the user's query history (data on the last 5 queries is output).

## Principle of communication with bot
When selecting commands (/lowprice, /highprice, /bestdeal) the bot alternately asks for hotel search data: location, 
check-in/check-out date (optional), price range and distances to the center (for the /bestdeal team), number of hotels 
to display, whether to display photos to hotels, as well as number of photos (if you agree to display photos).

For each hotel, the relevant data is provided for review.