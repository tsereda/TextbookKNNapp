from flask_restx import Resource, fields

def init_routes(api, ns_node, get_db_session):
    node_connection = api.model('NodeConnection', {
        'type': fields.String(required=True, description='Type of the relationship'),
        'targetNode': fields.Raw(required=True, description='Details of the connected node')
    })

    node_details = api.model('NodeDetails', {
        'id': fields.Integer(required=True, description='ID of the node'),
        'properties': fields.Raw(required=True, description='Properties of the node'),
        'connections': fields.List(fields.Nested(node_connection), description='Connections to other nodes')
    })
    
    @ns_node.route('/<int:node_id>')
    class Node(Resource):
        @api.marshal_with(node_details)
        def get(self, node_id):
            """Get details of a specific node"""
            with get_db_session() as session:
                result = session.run(
                    "MATCH (n) WHERE id(n) = $node_id "
                    "OPTIONAL MATCH (n)-[r]->(related) "
                    "RETURN n, collect({relationType: type(r), node: related}) as connections",
                    node_id=node_id
                )
                record = result.single()
                if record:
                    node = record["n"]
                    connections = record["connections"]
                    return {
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
                    }
                api.abort(404, "Node not found")

    @ns_node.route('/initialize_knowledge_graph')
    class InitializeKnowledgeGraph(Resource):
        def post(self):
            """Initialize the knowledge graph"""
            with get_db_session() as session:
                session.run("""
                    CREATE (c1:Chapter {name: 'Chapter 1: Introduction'})
                    CREATE (c2:Chapter {name: 'Chapter 2: Basics'})
                    CREATE (p1:Problem {name: 'Problem 1.1', description: 'Describe the scientific method'})
                    CREATE (p2:Problem {name: 'Problem 2.1', description: 'Solve a basic equation'})
                    CREATE (c1)-[:CONTAINS]->(p1)
                    CREATE (c2)-[:CONTAINS]->(p2)
                """)
            return {"message": "Knowledge graph initialized"}, 200

    @ns_node.route('/get_knowledge_graph')
    class GetKnowledgeGraph(Resource):
        def get(self):
            """Get the entire knowledge graph"""
            with get_db_session() as session:
                result = session.run("""
                    MATCH (n)
                    OPTIONAL MATCH (n)-[r]->(m)
                    RETURN n, collect({relationType: type(r), target: m}) as connections
                """)
                graph = [
                    {
                        "node": dict(record["n"]),
                        "connections": [
                            {
                                "type": conn["relationType"],
                                "target": dict(conn["target"])
                            } for conn in record["connections"] if conn["target"] is not None
                        ]
                    } for record in result
                ]
            return {"graph": graph}, 200

    @ns_node.route('/get_chapters_and_problems')
    class GetChaptersAndProblems(Resource):
        def get(self):
            """Get all chapters and their associated problems"""
            with get_db_session() as session:
                result = session.run("""
                    MATCH (c:Chapter)-[:CONTAINS]->(p:Problem)
                    RETURN c.name as chapter, collect(p.name) as problems
                """)
                chapters = [{"chapter": record["chapter"], "problems": record["problems"]} for record in result]
            return {"chapters": chapters}, 200

    @ns_node.route('/get_chapter_questions/<string:chapter_name>')
    class GetChapterQuestions(Resource):
        def get(self, chapter_name):
            """Get all questions for a specific chapter"""
            with get_db_session() as session:
                result = session.run("""
                    MATCH (c:Chapter {name: $chapter_name})-[:CONTAINS]->(p:Problem)
                    RETURN p.name as problem, p.description as description
                """, chapter_name=chapter_name)
                questions = [{"problem": record["problem"], "description": record["description"]} for record in result]
            return {"questions": questions}, 200

    @ns_node.route('/get_similarity_scores/<string:problem_name>')
    class GetSimilarityScores(Resource):
        def get(self, problem_name):
            """Get similarity scores for a specific problem"""
            # This is a placeholder. In a real implementation, you'd use a similarity algorithm.
            with get_db_session() as session:
                result = session.run("""
                    MATCH (p1:Problem {name: $problem_name})
                    MATCH (p2:Problem)
                    WHERE p1 <> p2
                    RETURN p2.name as problem, rand() as similarity
                    ORDER BY similarity DESC
                    LIMIT 5
                """, problem_name=problem_name)
                scores = [{"problem": record["problem"], "similarity": record["similarity"]} for record in result]
            return {"scores": scores}, 200

    @ns_node.route('/get_relevant_nodes/<string:query>')
    class GetRelevantNodes(Resource):
        def get(self, query):
            """Get nodes relevant to a given query"""
            with get_db_session() as session:
                result = session.run("""
                    MATCH (n)
                    WHERE n.name CONTAINS $query OR n.description CONTAINS $query
                    RETURN n.name as name, labels(n)[0] as type
                    LIMIT 10
                """, query=query)
                nodes = [{"name": record["name"], "type": record["type"]} for record in result]
            return {"relevant_nodes": nodes}, 200

    @ns_node.route('/get_relevant_pages/<string:query>')
    class GetRelevantPages(Resource):
        def get(self, query):
            """Get relevant pages from PDFs based on a query"""
            with get_db_session() as session:
                result = session.run("""
                    MATCH (p:PDF)
                    WHERE p.content CONTAINS $query
                    RETURN p.name as pdf_name, p.content as content
                    LIMIT 5
                """, query=query)
                pages = [
                    {
                        "pdf_name": record["pdf_name"],
                        "excerpt": record["content"][:200] + "..."  # Return first 200 characters as an excerpt
                    } for record in result
                ]
            return {"relevant_pages": pages}, 200
        
    @ns_node.route('/clear_all_nodes')
    class ClearAllNodes(Resource):
        def post(self):
            """Clear all nodes and relationships from the database"""
            with get_db_session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            return {"message": "All nodes and relationships have been cleared"}, 200
