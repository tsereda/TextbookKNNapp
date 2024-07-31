from flask import Flask
from flask_restx import Api
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os
from routes import search, node, pdf

# Load environment variables
load_dotenv()

app = Flask(__name__)
api = Api(app, version='1.0', title='Knowledge Graph API',
          description='A simple API for interacting with a Neo4j knowledge graph')

# Neo4j connection details
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")  # Changed from NEO4J_USER to NEO4J_USERNAME
password = os.getenv("NEO4J_PASSWORD")

# Create a Neo4j driver instance
driver = GraphDatabase.driver(uri, auth=(user, password))

# Test the connection
def test_connection():
    with driver.session() as session:
        try:
            result = session.run("RETURN 1 AS num")
            record = result.single()
            if record and record["num"] == 1:
                print("Successfully connected to Neo4j database")
            else:
                print("Connected to Neo4j, but unexpected result")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {str(e)}")
            raise

test_connection()

def get_db_session():
    return driver.session()

# Define namespaces
ns_search = api.namespace('search', description='Search operations')
ns_node = api.namespace('node', description='Node operations')
ns_pdf = api.namespace('pdf', description='PDF operations')

# Initialize routes
search.init_routes(api, ns_search, get_db_session)
node.init_routes(api, ns_node, get_db_session)
upload_folder = pdf.init_routes(api, ns_pdf, get_db_session)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = upload_folder

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)