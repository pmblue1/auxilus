import sqlite3
import datetime
import random

def itemStr(item):
    if str(type(item)) == "<class 'str'>":
        item = f'"{item}"'
    return item
class Integer:
    def __init__(self):
        self.type = "INTEGER"
class Real:
    def __init__(self):
        self.type = "REAL"
class Text:
    def __init__(self):
        self.type = "TEXT"
class TypeStr:
    def __init__(self,value):
        self.type = value
class between:
    def __init__(self,value1,value2):
        self.value1 = value1
        self.value2 = value2
class like:
    def __init__(self,value):
        self.value = value
class is_not:
    def __init__(self,value):
        self.value = value
class sqliteObj:
    def __init__(self,filename,table=None):
        self.conn = sqlite3.connect(filename)
        self.conn.row_factory = sqlite3.Row
        if table == None:
            self.table = None
        else:
            self.table = self.set_table(table)

    def select_all(self,dict_mode=True,table=None):
        cur = self.conn.cursor()
        if table == None:
            if self.table == None:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cur.fetchall()
                if tables != []:
                    table = tables[0][0]
                else:
                    raise Exception("No table selected, and no tables were found.")
            else:
                table = self.table
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()

        if dict_mode:
            newRows = []
            for x in rows:
                newRows.append(dict(x))
            return newRows
        else:
            return rows

    def select(self,select,orderDict=None,op_and=True,limit=None,dict_mode=True,table=None):
        cur = self.conn.cursor()
        if table == None:
            if self.table == None:
                raise Exception("No table set.")
            else:
                table = self.table
        if str(type(select)) == "<class 'str'>":
            query = select
        else:
            if str(type(select)) != "<class 'dict'>":
                raise Exception("'select' must be either a dictionary or a query string")
            query = f'SELECT * FROM {table} WHERE'
            c = 0
            if op_and:
                op = "AND"
            else:
                op = "OR"
            for x in select:
                c += 1
                item = select[x]
                nStr = ''
                if str(type(item)) in ["<class '__main__.is_not'>","<class 'sqliteObj.is_not'>"]:
                    nStr = 'NOT '
                    item = item.value
                if str(type(item)) == "<class 'str'>":
                    item = f'"{item}"'
                    newItem = f'{nStr}{x} = {item}'
                elif str(type(item)) == "<class 'list'>":
                    itemLen = len(item)
                    newItem = f'{nStr}{x} IN ('
                    c1 = 0
                    for y in item:
                        if str(type(y)) == "<class 'str'>":
                            y = f'"{y}"'
                        c1 += 1
                        if c1 == itemLen:
                            newItem = f'{newItem}{y})'
                            break
                        else:
                            newItem = f'{newItem}{y},'
                elif str(type(item)) in ["<class '__main__.between'>","<class 'sqliteObj.between'>"]:
                    newItem = f'{nStr}{x} BETWEEN {item.value1} AND {item.value2}'
                elif str(type(item)) in ["<class '__main__.like'>","<class 'sqliteObj.like'>"]:
                    newItem = f"{nStr}{x} LIKE '{item.value}'"
                else:
                    newItem = f'{nStr}{x} = {item}'


                if c == 1:
                    query = f'{query} {newItem}'
                else:
                    query = f'{query} {op} {newItem}'

            if orderDict != None:
                c2 = 0
                for x in orderDict:
                    c2 += 1
                    if orderDict[x] in ['DESC',1]:
                        kw = 'DESC'
                    elif orderDict[x] in ['ASC',0]:
                        kw = 'ASC'
                    else:
                        raise Exception(f"value '{orderDict[x]}' for '{x}' key in orderDict is invalid. Try making it 1 for descending order, or 0 for ascending order.")
                    if c2 == len(orderDict):
                        orderStr = f'{x} {kw}'
                    else:
                        orderStr = f'{x} {kw}, '
                query = f'{query} ORDER BY {orderStr}'
            if limit != None:
                if str(type(limit)) != "<class 'int'>":
                    raise Exception("'limit' must be an integer")
                else:
                    query = f'{query} LIMIT {limit};'
            else:
                query = f'{query};'
        cur.execute(query)
        rows = cur.fetchall()
        
        if dict_mode:
            newRows = []
            for x in rows:
                newRows.append(dict(x))
            return newRows
        else:
            return rows

    def set_table(self,table=None):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        if table == None:
            if tables != []:
                table = tables[0][0]
            else:
                raise Exception("No table selected, and no tables were found.")
        else:
            tableList = []
            for x in tables:
                for y in x:
                    tableList.append(y)
            if table in tableList:
                self.table = table
            else:
                raise Exception("invalid table selection")
        return table

    def tables(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        tableList = []
        if tables != []:
            for x in tables:
                for y in x:
                    tableList.append(y)
        return tables
    
###################################################
    
    def update(self,update,where,op_and=True,table=None):
        cur = self.conn.cursor()

        updateQuery = 'SET'
        uC = 0
        updateLen = len(update)
        for x in update:
            uC += 1
            newUItem = update[x]
            if str(type(newUItem)) == "<class 'str'>":
                newUItem = f'"{newUItem}"'
            if uC == updateLen:
                updateQuery = f'{updateQuery} {x} = {newUItem}'
            else:
                updateQuery = f'{updateQuery} {x} = {newUItem},'
        
        if table == None:
            if self.table == None:
                raise Exception("No table set.")
            else:
                table = self.table
        if str(type(where)) == "<class 'str'>":
            whereQuery = where
        else:
            if str(type(where)) != "<class 'dict'>":
                raise Exception("'where' must be either a dictionary or a query string")
            whereQuery = 'WHERE'
            c = 0
            if op_and:
                op = "AND"
            else:
                op = "OR"
            for x in where:
                c += 1
                item = where[x]
                nStr = ''
                if str(type(item)) in ["<class '__main__.is_not'>","<class 'sqliteObj.is_not'>"]:
                    nStr = 'NOT '
                    item = item.value
                if str(type(item)) == "<class 'str'>":
                    item = f'"{item}"'
                    newItem = f'{nStr}{x} = {item}'
                elif str(type(item)) == "<class 'list'>":
                    itemLen = len(item)
                    newItem = f'{nStr}{x} IN ('
                    c1 = 0
                    for y in item:
                        if str(type(y)) == "<class 'str'>":
                            y = f'"{y}"'
                        c1 += 1
                        if c1 == itemLen:
                            newItem = f'{newItem}{y})'
                            break
                        else:
                            newItem = f'{newItem}{y},'
                elif str(type(item)) in ["<class '__main__.between'>","<class 'sqliteObj.between'>"]:
                    newItem = f'{nStr}{x} BETWEEN {item.value1} AND {item.value2}'
                elif str(type(item)) in ["<class '__main__.like'>","<class 'sqliteObj.like'>"]:
                    newItem = f"{nStr}{x} LIKE '{item.value}'"
                else:
                    newItem = f'{nStr}{x} = {item}'


                if c == 1:
                    whereQuery = f'{whereQuery} {newItem}'
                else:
                    whereQuery = f'{whereQuery} {op} {newItem}'

                query = f'UPDATE {table} {updateQuery} {whereQuery}'
                cur.execute(query)
        
    
    def insert(self,insert,table=None):
        cur = self.conn.cursor()
        
        if table == None:
            if self.table == None:
                raise Exception("No table set.")
            else:
                table = self.table

        columns = '('
        iCount = 0
        iLen = len(insert)
        for x in insert:
            iCount += 1
            if iLen == iCount:
                columns = f'{columns}{x})'
            else:
                columns = f'{columns}{x}, '

        values = '('
        iCount = 0
        for x in insert:
            iCount += 1
            x = itemStr(insert[x])
            if iLen == iCount:
                values = f'{values}{x})'
            else:
                values = f'{values}{x}, '

        query = f'INSERT INTO {table} {columns} VALUES {values};'

        cur.execute(query)
        

    def add_column(self,column,datatype,current=None,table=None):
        cur = self.conn.cursor()
        
        if table == None:
            if self.table == None:
                raise Exception("No table set.")
            else:
                table = self.table

        if str(type(datatype)) == "<class 'str'>":
            datatype = TypeStr(datatype)
            
        query = f'ALTER TABLE {table} ADD COLUMN {column} {datatype.type};'

        cur.execute(query)

        if current != None:
            cur.execute(f'UPDATE {table} SET {column} = {itemStr(current)};')
        

    def drop_column(self,column,table=None):
        cur = self.conn.cursor()
        
        if table == None:
            if self.table == None:
                raise Exception("No table set.")
            else:
                table = self.table

        if str(type(datatype)) == "<class 'str'>":
            datatype = TypeStr(datatype)
            
        query = f'ALTER TABLE {table} DROP COLUMN {column};'

        cur.execute(query)

    def create_table(self,table):
        cur = self.conn.cursor()
        query = f'CREATE TABLE {table} (id INTEGER NOT NULL, PRIMARY KEY(id AUTOINCREMENT));'
        cur.execute(query)
        if self.table == None:
            self.table = table

    def drop_table(self,table=None):
        cur = self.conn.cursor()
        
        if table == None:
            if self.table == None:
                raise Exception("No table set.")
            else:
                table = self.table

        query = f'DROP TABLE {table};'
        cur.execute(query)

    def delete(self,delete,op_and=True,table=None):
        cur = self.conn.cursor()
        if table == None:
            if self.table == None:
                raise Exception("No table set.")
            else:
                table = self.table
                
        if str(type(delete)) == "<class 'str'>":
            query = delete
        else:
            if str(type(delete)) != "<class 'dict'>":
                raise Exception("'delete' must be either a dictionary or a query string")
            query = f'DELETE FROM {table} WHERE'
            c = 0
            if op_and:
                op = "AND"
            else:
                op = "OR"
            for x in delete:
                c += 1
                item = delete[x]
                nStr = ''
                if str(type(item)) in ["<class '__main__.is_not'>","<class 'sqliteObj.is_not'>"]:
                    nStr = 'NOT '
                    item = item.value
                if str(type(item)) == "<class 'str'>":
                    item = f'"{item}"'
                    newItem = f'{nStr}{x} = {item}'
                elif str(type(item)) == "<class 'list'>":
                    itemLen = len(item)
                    newItem = f'{nStr}{x} IN ('
                    c1 = 0
                    for y in item:
                        if str(type(y)) == "<class 'str'>":
                            y = f'"{y}"'
                        c1 += 1
                        if c1 == itemLen:
                            newItem = f'{newItem}{y})'
                            break
                        else:
                            newItem = f'{newItem}{y},'
                elif str(type(item)) in ["<class '__main__.between'>","<class 'sqliteObj.between'>"]:
                    newItem = f'{nStr}{x} BETWEEN {item.value1} AND {item.value2}'
                elif str(type(item)) in ["<class '__main__.like'>","<class 'sqliteObj.like'>"]:
                    newItem = f"{nStr}{x} LIKE '{item.value}'"
                else:
                    newItem = f'{nStr}{x} = {item}'


                if c == 1:
                    query = f'{query} {newItem}'
                else:
                    query = f'{query} {op} {newItem}'

        cur.execute(query)
        
###################################################

    def commit(self):
        self.conn.commit()

    def cursor(self):
        return self.conn.cursor()

    def execute(self,query):
        cur = self.conn.cursor()
        return cur.execute(query)
