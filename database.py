#!/usr/bin/env python3

import logging
import sys

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

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
            session.execute_read(self._merge_file, filename, created)

    @staticmethod
    def _merge_file(tx, filename, created):
        query = (
            "MERGE (f:File {filename: $filename, created: $created}) "
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
            "WHERE f.filename=$filename AND datetime(f.created) < datetime(ff.created) AND NOT exists((f)-[:PRECEEDS]->()) "
            "RETURN ff.filename "
            "ORDER BY ff.created "
        )
        result = tx.run(query, filename=filename)
        return result.value("ff.filename")
    
    def connect_file_to_succesor(self, filename, filename_succ):
        with self.driver.session() as session:
            result = session.execute_write(self._connect_file_to_succesor, filename, filename_succ)
            return result

    @staticmethod
    def _connect_file_to_succesor(tx, filename, filename_succ):
        query = (
            "MATCH (f:File) "
            "MATCH (ff:File) "
            "WHERE f.filename=$filename AND ff.filename=$filename_succ "
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
            "WHERE f.filename=$filename AND datetime(f.created) > datetime(ff.created) AND NOT exists((f)<-[:PRECEEDS]-()) "
            "RETURN ff.filename "
            "ORDER BY ff.created DESC"
        )
        result = tx.run(query, filename=filename)
        return result.value("ff.filename")

    def connect_file_to_predecessor(self, filename, filename_pred):
        with self.driver.session() as session:
            session.execute_write(self._connect_file_to_predecessor, filename, filename_pred)

    @staticmethod
    def _connect_file_to_predecessor(tx, filename, filename_pred):
        query = (
            "MATCH (f:File) "
            "MATCH (ff:File) "
            "WHERE f.filename=$filename AND ff.filename=$filename_pred "
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
            "WHERE f.filename=$filename_pred AND NOT ff.filename=$filename "
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
            "RETURN f.filename AS filename "
            "ORDER BY f.created "
        )
        result = tx.run(query)
        return [row["filename"] for row in result]

    def merge_PA_TR(self, PA, TR, filename):
        with self.driver.session() as session:
            session.execute_write(self._merge_PA_TR, PA, TR, filename)

    @staticmethod
    def _merge_PA_TR(tx, PA, TR, filename):
        queryA = (
            "MERGE (f:File {filename:$filename}) "
            "MERGE (p:PA {core:$corePA}) "
            "MERGE (t:TR {core:$coreTR}) "
            "MERGE (f)-[:DEFINES]->(p)-[:SERVED_BY]->(t) "
            "SET p.company=$companyPA, p.variant=$variantPA, p.timetableyear=$yearPA, "
            "    t.company=$companyTR, t.variant=$variantTR, t.timetableyear=$yearTR "
        )
        # queryB = (
        #     "MATCH (p:PA {core:$corePA}) "
        #     "MATCH (t:TR {core:$coreTR}) "
        #     "SET p.company=$companyPA, p.variant=$variantPA, p.timetableyear=$yearPA, "
        #     "    t.company=$companyTR, t.variant=$variantTR, t.timetableyear=$yearTR "
        # )
        tx.run(queryA, corePA=PA["Core"], companyPA=PA["Company"], variantPA=PA["Variant"], yearPA=PA["TimetableYear"], coreTR=TR["Core"],  companyTR=TR["Company"], variantTR=TR["Variant"], yearTR=TR["TimetableYear"], filename = filename)
        # tx.run(queryB, corePA=PA["Core"], companyPA=PA["Company"], variantPA=PA["Variant"], yearPA=PA["TimetableYear"], coreTR=TR["Core"], companyTR=TR["Company"], variantTR=TR["Variant"], yearTR=TR["TimetableYear"])

    def merge_related_PA(self, PA, relatedPA):
        with self.driver.session() as session:
            session.execute_write(self._merge_related_PA, PA, relatedPA)

    @staticmethod
    def _merge_related_PA(tx, PA, relatedPA):
        query = (
            "MATCH (p:PA {core:$corePA}) "
            "MATCH (pr:PA {core:$coreRelatedPA}) "
            "MERGE (p)-[:RELATED]->(pr) "
        )
        tx.run(query, corePA=PA["Core"], coreRelatedPA=relatedPA["Core"])

if __name__ == "__main__":
    Database.enable_log(logging.INFO, sys.stdout)
    db = Database(login, password, uri)
    db.merge_file("PA_0054_--KADR299295_01_2022.xml", "2022-10-01T11:40:1")
    db.close()
