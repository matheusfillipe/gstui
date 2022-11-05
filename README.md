# Work in progress

# GSTUI

A Text User Interface for exploring Google Cloud Storage. Fast and cached.

## Intallation

Clone this repo and run `pip install .`

## Usage

Run `gstui` or `gstui -h` to see more options.

# Development

Be free to submit a PR. Check the formatting with flake8 and for new features try to write tests.

## Tests


```sh
poetry run tests
```

Or manually

```sh
poetry run pytest tests -n 4 -vvv
```

## TODO

- [ ] Don't rely on `time.sleep` for cache tests
- [ ] [urwid](https://github.com/urwid/urwid) UI

# Related Projects

* [gsutil](https://github.com/GoogleCloudPlatform/gsutil) A command line tool for interacting with cloud storage services. 
* [gcsfuse](https://github.com/GoogleCloudPlatform/gcsfuse) A user-space file system for interacting with Google Cloud Storage 
