# Gift tracker

A small local web app for keeping track of people's likes, dislikes, important dates, sizes, gift ideas, gift history, wishlist links and notes, so you can look through it when choosing a gift.

No dependencies beyond Python 3. Everything stays on your machine.

## Run

```sh
python3 serve.py
```

Then open <http://127.0.0.1:8765/>. Set `GIFTS_PORT` to use another port.

The server only listens on `127.0.0.1` and rejects requests from other origins.

## Data

- `people.json` holds everything and is created on first save. It's plain JSON, easy to back up or edit by hand.
- One backup per day goes to `backups/people-YYYY-MM-DD.json`, and the last 30 are kept.
- Both are in `.gitignore`.

## Features

- An upcoming strip with birthdays and other dates in the next 60 days, including ages
- Search across every field
- Likes and dislikes as tags
- Gift ideas with link and price; "Given" moves an idea into the history
- Gift history with occasion, date and reaction (👍 😐 👎)
- A warning when an idea matches something already given
- Saves automatically as you type
