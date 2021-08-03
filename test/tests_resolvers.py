import pytest
from graphqlserver import resolvers

def test_resolve_indicator_by_id():
    result = resolvers.resolve_indicator_by_id(None, None, 106483006625399508799825370466766658890)