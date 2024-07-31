from flask import request
from flask_restx import Resource, fields

def init_routes(api, ns_search, get_db_session):
    search_result = api.model('SearchResult', {
        'name': fields.String(required=True, description='Name of the node'),
        'type': fields.String(required=True, description='Type of the node')
    })

    @ns_search.route('/')
    class Search(Resource):
        @api.doc(params={'q': 'Search query'})
        @api.marshal_list_with(search_result)
        def get(self):
            """Search for nodes in the knowledge graph"""
            query = request.args.get('q', '')
            
            with get_db_session() as session:
                result = session.run(
                    "MATCH (n) WHERE n.name CONTAINS $query RETURN n.name AS name, labels(n) AS labels",
                    query=query
                )
                data = [{"name": record["name"], "type": record["labels"][0]} for record in result]
            
            return data