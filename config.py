
db = {
    'user': 'root',
    'password': 'test1234',
    'host': 'localhost',
    'port': 2656,
    'database': 'miniter'
}

DB_URL = f"python-backend-test.cu2iuzk6u67e.ap-northeast-2.rds.amazonaws.com"
JWT_SECRET_KEY = 'SUPER_SECRET_KEY'
JWT_EXP_DELTA_SECONDS = 7 * 24 * 60 * 60


test_db = {
    'user': 'test',
    'password': 'password',
    'host': 'localhost',
    'port': 2656,
    'database': 'test_db'
}

test_config = {
    'DB_URL': f"mysql+mysqldb://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY': 'SUPER_SECRET_KEY',
}