# imdb-id-to-country-mapper
A tool to map OMDb information to a list of input IMDb IDs 

# Instructions:
- add OMDb API key to omdb-api-key.txt (on one line, no empty line at the end of the file)
- add IMDb IDs (links that contain the ID work as well) to the input.txt file (one ID per line)
- The attributes_to_use.txt file determines the OMDB attributes (and their order) to process. The spelling (including lowercase/uppercase) has to match the OMDB API call
- install Python dependencies and run the script

# Install Python dependencies
With Pipenv installed:

```make deps```

or

```pipenv install```

Without Pipenv:

``pip install click requests``

# Run the script
Python version >= 3.7 required.

With Pipenv installed:

```make run```

or

```pipenv run python country-to-imdb-mapper.py```

Without Pipenv:

``python country-to-imdb-mapper.py``