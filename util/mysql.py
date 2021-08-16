
import sqlalchemy as sa


user='fib_user'
password='wim123'
host='192.168.2.173'
database='fib_data'

url = f"mysql+pymysql://{user}:{password}@{host}/{database}"

engine: sa.engine.Engine = sa.create_engine(url)

metadata = sa.MetaData(bind=engine, reflect=True)