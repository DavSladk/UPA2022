#!/usr/bin/env python3

import sys

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
        self.__initDB__() 
        while True:
            self.parse()
            self.confirmCont()


    def __initDB__(self):
        line = input("Do you want to download data? Y/N\n")
        if line.casefold() in self.negative:
            print("Checking local resource . . .")
            self.check_local_data()

        elif line.casefold() in self.positive:
            print("Downloading resources . . .")
            self.download_data()

        else:
            print('\nDidn\'t understand "', line,'"')
            print('Please try again')
            self.__initDB__()
    

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