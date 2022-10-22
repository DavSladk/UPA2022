#!/usr/bin/env python3

import sys

from yaml import parse
import parser
import database
import time

def main():
    print("Application")
    try:
        App()
    except KeyboardInterrupt:
        print('\n')
        sys.exit(0)


"""
TODO:
    Get data from website

    Search FROM and TO stations in DATE time
"""


""" TODO: date conversions to db format """

class Query():
    init_station = ''
    terminal_station = ''
    init_date_time = ''
    terminal_date_time = ''

    def load_initial_station(self):
        self.init_station = input("Please put starting station:\n")

    def load_terminal_station(self):
        self.terminal_station = input("Please put terminal station:\n")

    def load_since_date(self):
        self.init_date_time = input("Please put since date:\n")

    def load_to_date(self):
        self.terminal_date_time = input("Please put to date:\n")

    def get_initial_station(self):
        return self.init_station 

    def get_terminal_station(self):
        return self.terminal_station 

    def get_since_date(self):
        return self.init_date_time  

    def get_to_date(self):
        return self.terminal_date_time
    
    def search_connection(self, init_station, terminal_station, init_date_time):
        date = init_date_time.split('T')[0]
        init_time = init_date_time.split('T')[1]+".0+01:00"
        db = database.Database(self.login, self.password, self.uri)
        start_time = time.time()    
        result = db.get_connection(init_station, terminal_station, date, init_time)
        end_time = time.time()
        db.close()
        total_time = end_time - start_time
        return result, total_time

    def print_result(self, result, total_time):
        print('---------------------------------------')
        if len(result) == 0:
            print("No connection found.")        
        for station in result:
            print(f'{station["location"]} -- {station["time"]}')
        print('---------------------------------------')
        print(f'It took {total_time}s to complete this query.')
        print('---------------------------------------')

    def __init__(self, login, password, uri):
        self.login=login
        self.password=password
        self.uri=uri
        self.load_initial_station()
        self.load_terminal_station()
        self.load_since_date()
        result, total_time = self.search_connection(self.init_station, self.terminal_station, self.init_date_time)
        self.print_result(result, total_time)


class App():
    negative = {'no', 'n', 'q','quit','exit'}
    positive = {'yes', 'y', ''}

    def __init__(self):
        self.login = sys.argv[1]
        self.password = sys.argv[2]
        self.uri = sys.argv[3]
        self.__initDB__() 
        while True:
            self.parse()
            self.confirm_cont()


    def __initDB__(self):
        line = input("Do you want to download data? Y/N\n")
        if line.casefold() in self.positive:
            print("Downloading resources . . .")
            self.check_local_data()
        elif line.casefold() in self.negative:
            pass
        else:
            print('\nDidn\'t understand "', line,'"')
            print('Please try again')
            self.__initDB__()

        line = input("Do you want to load local data? Y/N\n")
        if line.casefold() in self.positive:
            print("Loading local data . . .")
            start_time = time.time()
            self.load_files_to_database()
            self.process_files()
            end_time = time.time()
            print(f'Time to init the database: {end_time-start_time} s')
        elif line.casefold() in self.negative:
            pass
        else:
            print('\nDidn\'t understand "', line,'"')
            print('Please try again')
            self.__initDB__()
        
    def process_files(self):
        db = database.Database(self.login, self.password, self.uri)
        for file in db.get_unprocessed_files():
            parsed = parser.parse_file("xml_data/"+file)
            if parsed["type"] == "normal":
                db.merge_PA_TR(parsed["ids"][0], parsed["ids"][1], parsed["filename"])
                if parsed["related"] is not None:
                    db.merge_related_PA(parsed["ids"][0], parsed["related"])
                
                for location,timing,info in zip(parsed["locations"], parsed["timings"], parsed["at_loc_info"]):
                    db.merge_stations(parsed["ids"][0], location, timing, info)
                
                db.merge_days(parsed["ids"][0], parsed["list_calendar"])
            else:
                db.merge_cancels(parsed["ids"][0], parsed["filename"])
                db.delete_canceled_days(parsed["ids"][0], parsed["list_calendar"])
                pass
        db.close()

    def load_files_to_database(self):
        db = database.Database(self.login, self.password, self.uri)
        for parsed in parser.parsed_data_generator_reduced():
            db.merge_file(parsed["filename"],parsed["creation"])

            successor = db.has_file_successor(parsed["filename"])            
            if len(successor) == 0:
                pass
            else:
                db.connect_file_to_succesor(parsed["filename"], successor[0])

            predeseccor = db.has_file_predecessor(parsed["filename"])
            if len(predeseccor) == 0:
                pass
            else:
                db.connect_file_to_predecessor(parsed["filename"], predeseccor[0])
                db.remove_predecessor_connections(parsed["filename"], predeseccor[0])

        db.close()


    def parse(self):
        Query(self.login, self.password, self.uri)



    def download_data(self):
        if (self.check_local_data()):
            return
        else:
            pass
        
    
    def check_local_data(self):
        pass
        return True


    def confirm_cont(self):
        line = input("Do you wish to continue?\n")
        if line.casefold() in self.negative:
            sys.exit(0)
    

    def load_valid_items(self):
        pass

    
    def print_result(self):
        pass






if __name__ == "__main__":
    main()