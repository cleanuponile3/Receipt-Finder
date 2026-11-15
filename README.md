# Receipt-Finder

A small Python project for searching shop events by timestamp. It uses binary search to find an exact event; if there is no exact match, the web app shows the closest event and how far away it is.

## Run the web app

Requires Python 3; no packages need to be installed.

```bash
python3 receipt_web.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. The page uses Tailwind CSS from its CDN, so an internet connection is needed for styling.

The sample event list is in `Receiptfinder.py`. You can also run the terminal version with `python3 Receiptfinder.py`.
