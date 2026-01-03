
def test_api_key(api_key):
    assert api_key == "MOCK_KEY1234"

def test_channel_handle(channel_handle):
    assert channel_handle == "MRCHEESE"

def test_mock_postgres_conn(mock_postgres_conn_vars):

    assert mock_postgres_conn_vars.login == "mock_user_name"
    assert mock_postgres_conn_vars.password == "mock_password"
    assert mock_postgres_conn_vars.host == "mock_host"
    assert mock_postgres_conn_vars.port == 5432
    assert mock_postgres_conn_vars.schema == "mock_db_name"

def test_dags_integrity(dagbag):
    # 1 DAG
    assert dagbag.import_errors == {}, f"Import errors found: {dagbag.import_errors}"
    print("="*20)
    print(dagbag.import_errors)

    # 2 DAG
    expected_dag_ids = ["produce_json", "update_db", "data_quality"]
    loaded_dag_ids = list(dagbag.dags.keys())
    print("="*20)
    print(dagbag.dags.keys())
    for dag_id in expected_dag_ids:
        assert dag_id in loaded_dag_ids, f"DAG '{dag_id}' is missing in the DagBag"

    # 3 DAG
    assert dagbag.size() == 3
    print("="*20)
    print(dagbag.size())

    # 4 DAG 
    expected_task_counts = {
        "produce_json": 5,
        "update_db": 3,
        "data_quality": 3,
    }

    print("="*20)
    for dag_id, dag in dagbag.dags.items():
        expected_count = expected_task_counts.get(dag_id)
        actual_count = len(dag.tasks)
        assert(
            expected_count == actual_count
        ), f"DAG '{dag_id}' has {actual_count} tasks, expected {expected_count}"
        print(dag_id, len(dag.tasks))

