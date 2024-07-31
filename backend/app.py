from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Neo4j connection details
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

# Create a Neo4j driver instance
driver = GraphDatabase.driver(uri, auth=(user, password))

def get_db_session():
    return driver.session()

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    
    with get_db_session() as session:
        result = session.run(
            "MATCH (n) WHERE n.name CONTAINS $query RETURN n.name AS name, labels(n) AS labels",
            query=query
        )
        data = [{"name": record["name"], "type": record["labels"][0]} for record in result]
    
    return jsonify(data)

@app.route('/api/node/<node_id>', methods=['GET'])
def get_node(node_id):
    with get_db_session() as session:
        result = session.run(
            "MATCH (n) WHERE id(n) = $node_id "
            "OPTIONAL MATCH (n)-[r]->(related) "
            "RETURN n, collect({relationType: type(r), node: related}) as connections",
            node_id=int(node_id)
        )
        record = result.single()
        if record:
            node = record["n"]
            connections = record["connections"]
            return jsonify({
                "id": node.id,
                "properties": dict(node),
                "connections": [
                    {
                        "type": conn["relationType"],
                        "targetNode": {
                            "id": conn["node"].id,
                            "properties": dict(conn["node"])
                        }
                    } for conn in connections if conn["node"] is not None
                ]
            })
        else:
            return jsonify({"error": "Node not found"}), 404

@app.route('/api/pdf/upload', methods=['POST'])
def upload_pdf():
    # This is a placeholder. You'll need to implement PDF handling logic.
    return jsonify({"message": "PDF upload not yet implemented"}), 501

if __name__ == '__main__':
    app.run(debug=True)