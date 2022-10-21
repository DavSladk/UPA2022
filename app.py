#!/usr/bin/env python3

import sys

from yaml import parse
import parser
import database

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
    
    def __init__(self):
        self.load_initial_station()
        self.load_terminal_station()
        self.load_since_date()
        self.load_to_date()


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
            self.confirmCont()


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
            self.load_files_to_database()
            self.process_files()
        elif line.casefold() in self.negative:
            pass
        else:
            print('\nDidn\'t understand "', line,'"')
            print('Please try again')
            self.__initDB__()
        
    def process_files(self):
        db = database.Database(self.login, self.password, self.uri)
        for file in db.get_unprocessed_files():
            # print(file)
            parsed = parser.parse_file("xml_data/"+file)
            if parsed["type"] == "normal":
                db.merge_PA_TR(parsed["ids"][0], parsed["ids"][1], parsed["filename"])
                if parsed["related"] is not None:
                    db.merge_related_PA(parsed["ids"][0], parsed["related"])
                # db.merge_stations()
                # db.merge_days()
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
        query = Query()


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