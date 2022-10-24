#!/usr/bin/env python3

import logging
from neo4j import GraphDatabase

class Database:
    """Class handling neo4j database"""
    def __init__(self, user, password, uri):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()
    
    @staticmethod
    def enable_log(level, output_stream):
        handler = logging.StreamHandler(output_stream)
        handler.setLevel(level)
        logging.getLogger("neo4j").addHandler(handler)
        logging.getLogger("neo4j").setLevel(level)
    
    def merge_file(self, filename, created):
        with self.driver.session() as session:
            session.execute_write(self._merge_file, filename, created)

    @staticmethod
    def _merge_file(tx, filename, created):
        query = (
            "MERGE (f:File {Filename: $filename, Created: $created}) "
        )
        tx.run(query, filename=filename, created=created)

    def has_file_successor(self, filename):
        with self.driver.session() as session:
            result = session.execute_read(self._has_file_successor, filename)
            return result

    @staticmethod
    def _has_file_successor(tx, filename):
        query = (
            "MATCH (f:File) "
            "MATCH (ff:File) "
            "WHERE f.Filename=$filename AND datetime(f.Created) < datetime(ff.Created) AND NOT exists((f)-[:PRECEEDS]->()) "
            "RETURN ff.Filename "
            "ORDER BY ff.Created "
        )
        result = tx.run(query, filename=filename)
        return result.value("ff.Filename")
    
    def connect_file_to_succesor(self, filename, filename_succ):
        with self.driver.session() as session:
            result = session.execute_write(self._connect_file_to_succesor, filename, filename_succ)
            return result

    @staticmethod
    def _connect_file_to_succesor(tx, filename, filename_succ):
        query = (
            "MATCH (f:File) "
            "MATCH (ff:File) "
            "WHERE f.Filename=$filename AND ff.Filename=$filename_succ "
            "MERGE (f)-[:PRECEEDS]->(ff) "
        )
        tx.run(query, filename=filename, filename_succ=filename_succ)
    
    def has_file_predecessor(self, filename):
        with self.driver.session() as session:
            result = session.execute_read(self._has_file_predecessor, filename)
            return result

    @staticmethod
    def _has_file_predecessor(tx, filename):
        query = (
            "MATCH (f:File) "
            "MATCH (ff:File) "
            "WHERE f.Filename=$filename AND datetime(f.Created) > datetime(ff.Created) AND NOT exists((f)<-[:PRECEEDS]-()) "
            "RETURN ff.Filename "
            "ORDER BY ff.Created DESC"
        )
        result = tx.run(query, filename=filename)
        return result.value("ff.Filename")

    def connect_file_to_predecessor(self, filename, filename_pred):
        with self.driver.session() as session:
            session.execute_write(self._connect_file_to_predecessor, filename, filename_pred)

    @staticmethod
    def _connect_file_to_predecessor(tx, filename, filename_pred):
        query = (
            "MATCH (f:File) "
            "MATCH (ff:File) "
            "WHERE f.Filename=$filename AND ff.Filename=$filename_pred "
            "MERGE (f)<-[:PRECEEDS]-(ff) "
        )
        tx.run(query, filename=filename, filename_pred=filename_pred)

    def remove_predecessor_connections(self, filename, filename_pred):
        with self.driver.session() as session:
            session.execute_write(self._remove_predecessor_connections, filename, filename_pred)

    @staticmethod
    def _remove_predecessor_connections(tx, filename, filename_pred):
        query = (
            "MATCH (f:File)-[r:PRECEEDS]->(ff:File) "
            "WHERE f.Filename=$filename_pred AND NOT ff.Filename=$filename "
            "DELETE r"
        )
        tx.run(query, filename=filename, filename_pred=filename_pred)

    def get_unprocessed_files(self):
        with self.driver.session() as session:
            result = session.execute_read(self._get_unprocessed_files)
            for row in result:
                yield row
    
    @staticmethod
    def _get_unprocessed_files(tx):
        query = (
            "MATCH (f:File) "
            "WHERE NOT EXISTS ( (f)-[:DEFINES]->() ) "
            "RETURN f.Filename AS Filename "
            "ORDER BY f.Created "
        )
        result = tx.run(query)
        return [row["Filename"] for row in result]

    def merge_PA_TR(self, PA, TR, filename, network, foreign):
        with self.driver.session() as session:
            session.execute_write(self._merge_PA_TR, PA, TR, filename, network, foreign)

    @staticmethod
    def _merge_PA_TR(tx, PA, TR, filename, network, foreign):
        queryA = (
            "MERGE (f:File {Filename:$filename}) "
            "MERGE (p:PA {Core:$corePA}) "
            "MERGE (t:TR {Core:$coreTR}) "
            "MERGE (f)-[:DEFINES]->(p)-[:SERVED_BY]->(t) "
            "SET p.Company=$companyPA, p.Variant=$variantPA, p.TimetableYear=$yearPA, "
            "    t.Company=$companyTR, t.Variant=$variantTR, t.TimetableYear=$yearTR, "
            "    p.Network=$network, "
            "    p.Foreign=$foreign "
        )
        tx.run(queryA,
            corePA=PA["Core"],
            companyPA=PA["Company"],
            variantPA=PA["Variant"],
            yearPA=PA["TimetableYear"],
            coreTR=TR["Core"],
            companyTR=TR["Company"],
            variantTR=TR["Variant"],
            yearTR=TR["TimetableYear"],
            filename = filename,
            network=str(network),
            foreign=str(foreign)
        )

    def merge_related_PA(self, PA, relatedPA):
        with self.driver.session() as session:
            session.execute_write(self._merge_related_PA, PA, relatedPA)

    @staticmethod
    def _merge_related_PA(tx, PA, relatedPA):
        query = (
            "MATCH (p:PA {Core:$corePA}) "
            "MATCH (pr:PA {Core:$coreRelatedPA}) "
            "MERGE (p)-[:RELATED]->(pr) "
        )
        tx.run(query, corePA=PA["Core"], coreRelatedPA=relatedPA["Core"])

    def merge_cancels(self, PA, filename):
        with self.driver.session() as session:
            session.execute_write(self._merge_cancels, PA, filename)

    @staticmethod
    def _merge_cancels(tx, PA, filename):
        query = (
            "MATCH (f:File {Filename:$filename}) "
            "MATCH (p:PA {Core:$core}) "
            "MERGE (f)-[:CANCELS]->(p) "
        )
        tx.run(query, filename=filename, core=PA["Core"])
    
    def merge_days(self, PA, calendarList):
        with self.driver.session() as session:
            for day in calendarList:
                session.execute_write(self._merge_days, PA, day)

    @staticmethod
    def _merge_days(tx, PA, day):
        query = (
            "MERGE (p:PA {Core:$core}) "
            "MERGE (d:Day {Date:$day}) "
            "MERGE (p)-[:GOES_IN]->(d) "
        )
        tx.run(query, day=day, core=PA["Core"])
    
    def delete_canceled_days(self, PA, calendarList):
        with self.driver.session() as session:
            for day in calendarList:
                session.execute_write(self._delete_canceled_days, PA, day)

    @staticmethod
    def _delete_canceled_days(tx, PA, day):
        query = (
            "MATCH (p:PA {Core:$core}) -[g:GOES_IN]-> (d:Day {Date:$day}) "
            "DELETE g "
        )
        tx.run(query, day=day, core=PA["Core"])
    
    def merge_stations(self, PA, location, timing, info):
        with self.driver.session() as session:
            session.execute_write(self._merge_stations, PA,location, timing, info)

    @staticmethod
    def _merge_stations(tx, PA, location, timing, info):
        query = (
            "MERGE (s:Station {LocationPrimaryCode:$LocationPrimaryCode, PrimaryLocationName:$PrimaryLocationName, CountryCodeISO:$CountryCodeISO}) "
            "MERGE (p:PA {Core:$Core}) "
            "MERGE (p)-[i:IS_IN]->(s) "
            "SET "
            "i.LocationSubsidiaryCode=$LocationSubsidiaryCode, "
            "i.AllocationCompany=$AllocationCompany, "
            "i.LocationSubsidiaryName=$LocationSubsidiaryName, "
            "i.ALA=$ALA, "
            "i.ALAoffset=$ALAoffset, "
            "i.ALD=$ALD, "
            "i.ALDoffset=$ALDoffset, "
            "i.DwellTime=$DwellTime, "
            "i.ResponsibleRU=$ResponsibleRU, "
            "i.ResponsibleIM=$ResponsibleIM, "
            "i.TrainType=$TrainType, "
            "i.TrafficType=$TrafficType, "
            "i.OperationalTrainNumber=$OperationalTrainNumber, "
            "i.TrainActivityType=$TrainActivityType, "
            "i.Network=$Network"
        )
        tx.run(query,
            LocationPrimaryCode=location["LocationPrimaryCode"],
            PrimaryLocationName=location["PrimaryLocationName"],
            CountryCodeISO=location["CountryCodeISO"],
            Core=PA["Core"],
            LocationSubsidiaryCode= location["LocationSubsidiaryIdentification"]["LocationSubsidiaryCode"],
            AllocationCompany=location["LocationSubsidiaryIdentification"]["AllocationCompany"],
            LocationSubsidiaryName=location["LocationSubsidiaryIdentification"]["LocationSubsidiaryName"],
            ALA=timing["Timing"][0]["Time"],
            ALAoffset=timing["Timing"][0]["Offset"],
            ALD=timing["Timing"][1]["Time"],
            ALDoffset=timing["Timing"][1]["Offset"],
            DwellTime=timing["DwellTime"],
            ResponsibleRU=info["ResponsibleRU"],
            ResponsibleIM=info["ResponsibleIM"],
            TrainType=info["TrainType"],
            TrafficType=info["TrafficType"],
            OperationalTrainNumber=info["OperationalTrainNumber"],
            TrainActivityType=info["TrainActivityType"],
            Network=str(info["NetworkSpecificParameter"])
        )
    
    def get_connection(self, init_station, terminal_station, date, time):
        with self.driver.session() as session:
            return session.execute_read(self._get_connection, init_station, terminal_station, date, time)

    @staticmethod
    def _get_connection(tx, init_station, terminal_station, date, time):
        query = (
            "MATCH (s:Station)<-[i:IS_IN]-(p:PA)-[ii:IS_IN]->(ss:Station) "
            "MATCH (p)-[:GOES_IN]->(d:Day) "
            "MATCH (sx:Station)<-[ix:IS_IN]-(p)-[ii:IS_IN]->(ss:Station) "
            "WHERE s.PrimaryLocationName=$station1 "
            "AND   ss.PrimaryLocationName=$station2 "
            "AND   time(i.ALA) > time($time) "
            "AND   time(ii.ALA) > time(i.ALA) "
            "AND   d.Date=$date "
            "AND   time(ix.ALA) > time(i.ALA) "
            "AND   time(ix.ALA) < time(ii.ALA) "
            "AND   '0001' IN i.TrainActivityType AND i.TrainType='1' "
            "AND   '0001' IN ii.TrainActivityType AND ii.TrainType='1' "
            "RETURN s.PrimaryLocationName, i.ALA, sx.PrimaryLocationName, ix.ALA, ss.PrimaryLocationName, MIN(ii.ALA) " 
        )
        result = tx.run(query, station1=init_station, station2=terminal_station, time=time, date=date)
        to_return = []
        start = {}
        end = {}
        for row in result:
            if not end == {"location":row["ss.PrimaryLocationName"], "time":row["ii.ALA"].split('.')[0]} and end:
                break
            start = {"location":row["s.PrimaryLocationName"], "time":row["i.ALA"].split('.')[0]}
            to_return.append({"location":row["sx.PrimaryLocationName"], "time":row["ix.ALA"].split('.')[0]})
            end = {"location":row["ss.PrimaryLocationName"], "time":row["ii.ALA"].split('.')[0]}
        
        if len(to_return) == 0:
            return to_return

        to_return.append(end)
        to_return = [start] + to_return

        return to_return
