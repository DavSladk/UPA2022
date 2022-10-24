#!/usr/bin/env python3

import sys

import parser
import database
import time
import download
import query

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
            self.download_data()
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
                db.merge_PA_TR(parsed["ids"][0], parsed["ids"][1], parsed["filename"], parsed["network"], parsed["header"])
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
        query.Query(self.login, self.password, self.uri)

    def confirm_cont(self):
        line = input("Do you wish to continue?\n")
        if line.casefold() in self.negative:
            sys.exit(0)
    
    def download_data():
        download.main()


def main():
    try:
        App()
    except KeyboardInterrupt:
        print('\n')
        sys.exit(0)

if __name__ == "__main__":
    main()