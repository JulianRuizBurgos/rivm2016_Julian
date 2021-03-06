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
        
    result = resolvers.resolve_indicator_by_id(None, None, 273737595174257546810686733816717221194)

    assert expected == result

def test_resolve_indicators():
    result = resolvers.resolve_indicators(None, None)

def test_resolve_entry_by_id():

    expected = {
        "id": 27204426082222136872375596879506152778,
        "productName": "Varkenskarbonade schouder",
        "geography": "NL",
        "unit": "kg"
    }

    result = resolvers.resolve_entry_by_id(None, None, 27204426082222136872375596879506152778)

    assert expected == result

def test_resolve_entries():
    result = resolvers.resolve_entries(None, None)

def test_resolve_impact():

    expected = {
        "coefficient" : 0.0
    }

    result = resolvers.resolve_impact(None, None, 41032945853956639112186813749937937738, 41008384806664567109155347110384999754)
    print(result)
    assert result["coefficient"] == expected["coefficient"]
