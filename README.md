# Quantopian-Algo
This a personal learning project trading algorithm.

1)A pipline of stocks that meet the following criteria is created:
* market cap under 5 billion.
* price is under the 30 day simple moving average .
* price is under 15$.
* interday stock prices are generally clean, meaning the interday prices are continuous and liquid to avoid high spreads and orders not filling.

2) Stock purchase based on the pipeline, rebalance once a week.
* purchase occures when price is whithin the 30% to 60% of the yearly price range.
* if the stock is down to under 15% of the yearly range or not in pipeline, exit (stop loss).
* if the stock is up to 90% of the yearly range, exit (take profit).

What I am idealy trying to achieve is this:

![2020-09-09_0158](https://user-images.githubusercontent.com/66104129/92535543-20c79180-f240-11ea-8dd2-dc60218a439a.png)


this current algorithm still needs a lot of refining!:

![algo1result](https://user-images.githubusercontent.com/66104129/92535856-e1e60b80-f240-11ea-98d9-eac64b7d8714.jpg)

Disclaimer: This algorithm is created for learning purposes, this is by no means a strategy for trying in a real cash broker account.
