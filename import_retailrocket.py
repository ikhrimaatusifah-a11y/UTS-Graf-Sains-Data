"""Tugas 1.3: impor RetailRocket events.csv ke Neo4j secara batch."""
import argparse
import os
from pathlib import Path
import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm


def create_constraints(session):
    session.run('CREATE CONSTRAINT visitor_id_unique IF NOT EXISTS FOR (v:Visitor) REQUIRE v.visitorId IS UNIQUE').consume()
    session.run('CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.itemId IS UNIQUE').consume()


def import_batch(tx, batch):
    # Semua event dibuat sesuai tiga relationship yang diminta soal.
    query = '''
    UNWIND $batch AS row
    MERGE (v:Visitor {visitorId: row.visitorid})
    MERGE (i:Item {itemId: row.itemid})
    WITH v, i, row
    FOREACH (_ IN CASE WHEN row.event = 'view' THEN [1] ELSE [] END |
        CREATE (v)-[:VIEWED {timestamp: row.timestamp}]->(i))
    FOREACH (_ IN CASE WHEN row.event = 'addtocart' THEN [1] ELSE [] END |
        CREATE (v)-[:ADDED_TO_CART {timestamp: row.timestamp}]->(i))
    FOREACH (_ IN CASE WHEN row.event = 'transaction' THEN [1] ELSE [] END |
        CREATE (v)-[:BOUGHT {timestamp: row.timestamp, transactionId: row.transactionid}]->(i))
    '''
    tx.run(query, batch=batch).consume()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='data', help='Folder berisi events.csv')
    parser.add_argument('--bolt', default=os.getenv('NEO4J_URI', 'bolt://localhost:7687'))
    parser.add_argument('--user', default=os.getenv('NEO4J_USER', 'neo4j'))
    parser.add_argument('--password', default=os.getenv('NEO4J_PASSWORD'))
    parser.add_argument('--batch-size', type=int, default=1000)
    parser.add_argument('--limit', type=int, default=0, help='0=semua data; 5=tes 5 baris')
    args = parser.parse_args()
    if not args.password:
        parser.error('Set NEO4J_PASSWORD pada environment atau gunakan --password')
    if args.batch_size <= 0 or args.limit < 0:
        parser.error('--batch-size harus positif dan --limit tidak negatif')
    path = Path(args.source) / 'events.csv'
    if not path.is_file():
        parser.error(f'File tidak ditemukan: {path}')
    driver = GraphDatabase.driver(args.bolt, auth=(args.user, args.password))
    try:
        driver.verify_connectivity()
        with driver.session(database='neo4j') as session:
            create_constraints(session)
            reader = pd.read_csv(path, chunksize=args.batch_size,
                                 dtype={'visitorid': 'int64', 'itemid': 'int64', 'timestamp': 'int64'})
            imported = 0
            for chunk in tqdm(reader, desc='Mengimpor batch'):
                if args.limit:
                    chunk = chunk.iloc[:args.limit - imported]
                if chunk.empty:
                    break
                chunk['transactionid'] = chunk['transactionid'].fillna('').astype(str)
                rows = chunk.to_dict(orient='records')
                session.execute_write(import_batch, rows)
                imported += len(rows)
                if args.limit and imported >= args.limit:
                    break
            print(f'Proses impor berhasil: {imported} baris diproses.')
    finally:
        driver.close()


if __name__ == '__main__':
    main()
