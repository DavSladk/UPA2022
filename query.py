import database
import time

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
