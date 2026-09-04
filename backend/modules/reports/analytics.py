from backend.config import get_settings


def analytics_status():
    settings=get_settings()
    try:
        import clickhouse_connect
        client=clickhouse_connect.get_client(host=settings.clickhouse_host,port=settings.clickhouse_port,database=settings.clickhouse_database,connect_timeout=2,send_receive_timeout=3)
        tables=client.query("SHOW TABLES").result_rows
        counts={name:client.query(f"SELECT count() FROM {name}").first_row[0] for (name,) in tables}
        return {"status":"ok","engine":"ClickHouse","database":settings.clickhouse_database,"tables":counts}
    except Exception as error:
        return {"status":"unavailable","engine":"ClickHouse","database":settings.clickhouse_database,"message":str(error)[:160]}
