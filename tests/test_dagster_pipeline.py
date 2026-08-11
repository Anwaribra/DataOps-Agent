import importlib.util
from pathlib import Path
from dagster import Definitions

def load_dagster_definitions():
    def_path = Path(__file__).resolve().parent.parent / "dagster" / "definitions.py"
    spec = importlib.util.spec_from_file_location("local_dagster_defs", def_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.defs

def test_dagster_definitions_load():
    defs = load_dagster_definitions()
    assert isinstance(defs, Definitions)
    
    # Check assets registered in asset graph
    asset_graph = defs.resolve_asset_graph()
    asset_keys = [key.to_user_string() for key in asset_graph.get_all_asset_keys()]
    assert "raw_ecommerce_data" in asset_keys
    assert "dbt_transformation_models" in asset_keys
    assert "dbt_test_results" in asset_keys

def test_dagster_checks_registered():
    defs = load_dagster_definitions()
    checks = defs.asset_checks
    assert len(checks) > 0
