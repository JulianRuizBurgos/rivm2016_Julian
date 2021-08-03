import pytest
from graphqlserver import resolvers

def test_resolve_indicator_by_id():

    expected = {
        'id': 247952362168809575136085981609942424906, 
        'method': 'cumulative energy demand',
        'category': 'fossil', 
        'indicator': 'non-renewable energy resources, fossil', 
        'units': 'MJ-Eq'
        }
        
    result = resolvers.resolve_indicator_by_id(None, None, 247952362168809575136085981609942424906)

    assert expected == result

def test_resolve_indicators():
    result = resolvers.resolve_indicators(None, None)
