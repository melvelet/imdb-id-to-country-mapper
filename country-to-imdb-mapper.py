import copy
import csv

import click as click
import requests


class CountryToIMDbMapper:
    def __init__(self):
        self.omdb_api_key = self.__get_omdb_api_key()
        self.attributes_to_use = self.__get_list_of_attributes_to_use()
        self.mappings = self.__get_mappings_from_file()

    def __get_omdb_api_key(self):
        with open('omdb-api-key.txt', 'r') as file:
            return file.read()

    def __get_list_of_attributes_to_use(self):
        with open('attributes_to_use.txt', 'r') as file:
            return file.read().splitlines()

    def __get_mappings_from_file(self):
        mappings = dict()
        try:
            with open('mappings.csv', 'r') as file:
                reader = csv.reader(file, delimiter=';')
                mappings_header = next(reader)
                for row in reader:
                    imdb_id = row[0]
                    mappings[imdb_id] = dict()
                    for i, cell in enumerate(row[1:]):
                        mappings[imdb_id][mappings_header[i + 1]] = cell
        finally:
            return mappings

    def write_results_to_file(self, results):
        results_writer = csv.writer(open('results.csv', 'w+'), delimiter=';')
        for row in results:
            results_writer.writerow(row)

    def __get_input_imdb_ids(self):
        result = list()
        with open('input.txt') as file:
            for line in file.readlines():
                result.append(self.__get_imdb_id_from_link(line))
        return result

    def __get_imdb_id_from_link(self, link):
        imdb = [content for content in link.split('/') if content.startswith('tt')]
        return str.rstrip(imdb[0]) if imdb else None

    def get_attributes_from_omdb(self, imdb_id):
        req_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={self.omdb_api_key}"
        response = requests.post(req_url)
        result = dict()
        if 'Error' in response.json():
            print(response.json()['Error'])
            return response.json()['Error']
        for attribute in self.attributes_to_use:
            result[attribute] = response.json()[attribute]
        return result

    def all_necessary_attributes_in_movie_info(self, movie_info):
        if not movie_info:
            return False
        for attribute in self.attributes_to_use:
            if attribute not in movie_info:
                return False
        return True

    def __get_movie_info_dict(self, input_ids):
        result = dict()
        api_limit_exceeded = False
        api_calls = 0
        for imdb_id in input_ids:
            movie_info = None
            if imdb_id in self.mappings:
                movie_info = self.mappings[imdb_id]
            if not api_limit_exceeded and not self.all_necessary_attributes_in_movie_info(movie_info):
                if api_calls and api_calls % 10 == 0:
                    print(api_calls, 'API calls executed.')
                api_calls += 1
                movie_info = self.get_attributes_from_omdb(imdb_id)
                if type(movie_info) == str:
                    api_limit_exceeded = True
            if movie_info and type(movie_info) != str:
                result[imdb_id] = movie_info

        return result

    def write_movie_info_file(self, input_ids, movie_info_dict):
        with open('results.csv', 'w+') as file:
            results_writer = csv.writer(file, delimiter=';')
            for imdb_id in input_ids:
                row = list([imdb_id])
                for attribute in self.attributes_to_use:
                    row.append(movie_info_dict.get(imdb_id, dict()).get(attribute, ''))
                results_writer.writerow(row)

    def write_new_mappings(self, movie_info_dict):
        new_mappings = copy.deepcopy(self.mappings)
        for imdb_id, entry in movie_info_dict.items():
            new_mappings[imdb_id] = entry
        with open('mappings.csv', 'w+') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['imdbID'] + self.attributes_to_use)
            for imdb_id, entry in new_mappings.items():
                row = list([imdb_id])
                for attribute in self.attributes_to_use:
                    row.append(entry.get(attribute, ''))
                writer.writerow(row)

    def process_input_ids(self):
        input_ids = self.__get_input_imdb_ids()
        movie_info_dict = self.__get_movie_info_dict(input_ids)
        self.write_movie_info_file(input_ids, movie_info_dict)
        self.write_new_mappings(movie_info_dict)


@click.command()
@click.option("-c", "--country", type=str, required=False, help='Filter results to only include the specified country')
def go(country):
    mapper = CountryToIMDbMapper()
    mapper.process_input_ids()
    # result = mapper.map_countries_to_imdb_ids(country=country)
    # mapper.write_results_to_file(result)
    print('Results written to file.')


if __name__ == '__main__':
    go()
