from ariadne import gql, graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify
from graphqlserver import resolvers
from loggerwrapper import Logger

app = Flask(__name__)


type_defs = load_schema_from_path("schemas/schema.gql")
query = QueryType()

indicator = ObjectType('Indicator')
entry = ObjectType('Entry')
impact = ObjectType('Impact')
geography = ObjectType('Geography')

query.set_field('indicator', resolvers.resolve_indicator_by_id)
query.set_field('indicators', resolvers.resolve_indicators)
query.set_field('entry', resolvers.resolve_entry_by_id)
query.set_field('entries', resolvers.resolve_entries)
query.set_field('impact', resolvers.resolve_impact)

entry.set_field('geography', resolvers.resolve_geography)
entry.set_field('impact', resolvers.resolve_impact_related_to_entry)

impact.set_field('indicator', resolvers.resolve_indicator_for_impact)
impact.set_field('entry', resolvers.resolve_entry_for_impact)


schema = make_executable_schema(type_defs, [indicator, entry, impact, geography, query])

@app.route('/graphql', methods=['GET'])
def playground():
    return PLAYGROUND_HTML, 200

@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
    schema,
    data,
    context_value=None,
    debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code
