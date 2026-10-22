"""Tugas 1.2: contoh node Person dan relationship KNOWS."""
import os
from neo4j import GraphDatabase

URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
USER = os.getenv('NEO4J_USER', 'neo4j')
PASSWORD = os.environ['NEO4J_PASSWORD']

with GraphDatabase.driver(URI, auth=(USER, PASSWORD)) as driver:
    driver.verify_connectivity()
    for friend in ('Guinevere', 'Lancelot', 'Merlin'):
        driver.execute_query(
            'MERGE (a:Person {name: $name}) MERGE (b:Person {name: $friend}) MERGE (a)-[:KNOWS]->(b)',
            name='Arthur', friend=friend, database_='neo4j')
    records, _, _ = driver.execute_query(
        'MATCH (:Person {name: $name})-[:KNOWS]->(f:Person) RETURN f.name AS friend ORDER BY friend',
        name='Arthur', database_='neo4j')
    print('Teman Arthur:')
    for record in records:
        print(record['friend'])
