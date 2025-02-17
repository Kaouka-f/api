import psycopg2
from psycopg2 import sql
import os

class PGManager:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.conn_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor()
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

    def disconnect(self):
        try:
            self.cursor.close()
            self.conn.close()
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

    def version(self):
        try:
            self.cursor.execute("SELECT version();")
            db_version = self.cursor.fetchone()
            print(f"Database version: {db_version}")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

    def createTable(self, tableName, columns):
        column_definitions = [
            sql.SQL("{} {}").format(sql.Identifier(col_name), sql.SQL(data_type))
            for col_name, data_type in columns
        ]
        create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {table} ({fields});").format(
            table=sql.Identifier(tableName),
            fields=sql.SQL(', ').join(column_definitions)
        )
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

    def insertQuery(self, tableName, key, value):
        insert_query = sql.SQL("INSERT INTO {table} ({field}) VALUES (%s)").format(
            table=sql.Identifier(tableName),
            field=sql.Identifier(key)
        )
        try:
            self.cursor.execute(insert_query, (value,))
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            self.conn.rollback()
            raise e
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            raise e

    def updateById(self, tableName, idValue, fieldName, value):
        update_query = f"UPDATE {tableName} SET {fieldName} = %s WHERE id = %s"
        try:
            # Execute the update query with the new value and id
            self.cursor.execute(update_query, (value, idValue))
            self.conn.commit()
            print(f"{fieldName} updated successfully for id {idValue}")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            self.conn.rollback()
            raise e
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            raise e

    def deleteQuery(self, tableName, key, field):
        delete_query = sql.SQL("DELETE FROM {table} WHERE {field} = %s").format(
            table=sql.Identifier(tableName),
            field=sql.Identifier(key)
        )

        self.cursor.execute(delete_query, (field,))
        self.conn.commit()

    # TODO: getQuery should return a single record or a list of records with key
    def getQuery(self, tableName, key, field):
        select_query = sql.SQL("SELECT * FROM {table} WHERE {field} = %s").format(
            table=sql.Identifier(tableName),
            field=sql.Identifier(key)
        )

        self.cursor.execute(select_query, (field,))
        records = self.cursor.fetchall()

        return records

    def mapForeignKey(self, tableName, foreignKey, refTable, refKey):
        alter_table_query = sql.SQL("ALTER TABLE {table} ADD FOREIGN KEY ({field}) REFERENCES {refTable} ({refKey})").format(
            table=sql.Identifier(tableName),
            field=sql.Identifier(foreignKey),
            refTable=sql.Identifier(refTable),
            refKey=sql.Identifier(refKey)
        )

        self.cursor.execute(alter_table_query)
        self.conn.commit()

    def tableExists(self, table_name):
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (table_name,))
        return self.cursor.fetchone()[0]

    def printTable(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()

        if rows:
            # Print column names
            col_names = [desc[0] for desc in self.cursor.description]
            print(','.join(col_names))

            # Print rows
            for row in rows:
                print(','.join(map(str, row)))
        else:
            print(f"No data found in table '{table_name}'.")

# EXAMPLE
# db = PGManager('kaouka_db', 'kaoukakeet', 'indestructible')
# db.connect()
# columns = [
#     ('id', 'SERIAL PRIMARY KEY'),
#     ('name', 'VARCHAR(100)'),
#     ('age', 'INTEGER'),
#     ('email', 'VARCHAR(100)'),
# ]
# db.createTable('test2', columns)
# db.printTable('test2')
# db.insertQuery('test2', 'id', '12345')
# db.updateById('test2', '12345', 'name', 'John')
# print(db.getQuery('test2', 'id', '12345'))
# db.deleteQuery('test2', 'id', '123456')


# data = {
#     'id': '12345',
#     'name': 'John Doe',
#     'age': 30,
#     'email': 'johndoe@example.com'
# }

# db.disconnect()