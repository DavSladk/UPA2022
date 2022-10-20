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
            "MERGE (f:File {filename: $filename, created: $created})"
            "ON CREATE SET f.processed=false"
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
            result = session.execute_write(self._connect_file_to_predecessor, filename, filename_pred)
            return result

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
            result = session.execute_write(self._remove_predecessor_connections, filename, filename_pred)
            return result

    @staticmethod
    def _remove_predecessor_connections(tx, filename, filename_pred):
        query = (
            "MATCH (f:File)-[r:PRECEEDS]->(ff:File) "
            "WHERE f.filename=$filename_pred AND NOT ff.filename=$filename "
            "DELETE r"
        )
        tx.run(query, filename=filename, filename_pred=filename_pred)

if __name__ == "__main__":
    Database.enable_log(logging.INFO, sys.stdout)
    db = Database(login, password, uri)
    db.merge_file("PA_0054_--KADR299295_01_2022.xml", "2022-10-01T11:40:1")
    db.close()
