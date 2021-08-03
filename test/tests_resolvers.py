import pytest
from graphqlserver import resolvers

def test_resolve_indicator_by_id():
    resolvers.resolve_indicator_by_id(None, None, 100189813532485611953517214780313935178)