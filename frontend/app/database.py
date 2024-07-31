from py2neo import Graph

def get_db():
    return Graph("bolt://neo4j:7687", auth=("neo4j", "password"))
