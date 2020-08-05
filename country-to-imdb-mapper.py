import csv
import requests


class CountryToIMDbMapper:
    def __init__(self):
        self.omdb_api_key = self.__get_omdb_api_key()
        self.mappings = self.__get_mappings_from_file()
        self.writer = csv.writer(open('mappings.csv', 'a+'), delimiter=';')

    def __get_omdb_api_key(self):
        with open('omdb-api-key.txt') as file:
            return file.read()

    def __get_mappings_from_file(self):
        mappings = dict()
        try:
            with open('mappings.csv', 'r') as file:
                reader = csv.reader(file, delimiter=';')
                for line in reader:
                    imdb_id = line[0]
                    countries = line[1]
                    mappings[imdb_id] = countries
        finally:
            return mappings

    def __write_new_mapping_to_file(self, imdb_id, countries):
        self.writer.writerow([imdb_id, countries])


    def write_results_to_file(self, results):
        results_writer = csv.writer(open('results.csv', 'w+'), delimiter=';')
        for row in results:
            results_writer.writerow(row)

    def __yield_input_imdb_ids(self):
        with open('input.txt') as file:
            for line in file.readlines():
                yield self.__get_imdb_id_from_link(line)

    def __get_imdb_id_from_link(self, link):
        imdb = [content for content in link.split('/') if content.startswith('tt')]
        return str.rstrip(imdb[0]) if imdb else None

    def get_country_from_omdb(self, imdb_id):
        req_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={self.omdb_api_key}"
        response = requests.post(req_url)
        print(response.json())
        if 'Error' in response.json():
            print(response.json()['Error'])
            return None
        if 'Country' in response.json():
            return response.json()['Country']
        return ''

    def map_countries_to_imdb_ids(self):
        result = list()
        api_limit_exceeded = False
        for imdb_id in self.__yield_input_imdb_ids():
            countries = ''
            print(imdb_id, imdb_id in self.mappings)
            if imdb_id in self.mappings:
                countries = self.mappings[imdb_id]
            elif not api_limit_exceeded:
                countries = self.get_country_from_omdb(imdb_id)
                if countries is None:
                    api_limit_exceeded = True
                if countries:
                    self.__write_new_mapping_to_file(imdb_id, countries)

            result.append([imdb_id, countries])
        return result


if __name__ == '__main__':
    mapper = CountryToIMDbMapper()
    result = mapper.map_countries_to_imdb_ids()
    print(result)
    mapper.write_results_to_file(result)
