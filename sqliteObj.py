import sqlite3
import datetime
import random
import sys
import traceback



class TableNotSet(Exception):
    """Exception raised when a table is not set."""
    def __init__(self):
        super().__init__("Table not set. No default is set and table not specified.")
class ColumnNotFound(Exception):
    """Exception raised when a table is not set."""
    def __init__(self,given,table):
        super().__init__(f"Column '{given}' is not in table '{table}'")        
class InvalidKeyResponse(Exception):
    """Exception raised when given key function gives invalid response in a custom method."""
    def __init__(self,given,key):
        super().__init__(f"Provided key function '{key.__name__}' gave '{str(type(given))}' type response. Please be sure that your key function only returns Boolean values.")
class ModuleOperationError(Exception):
    """Exception raised when this module messes up essentially. When there is an error with an exection, the query that caused the error, and the exception itself, are returned."""
    def __init__(self,query,trc):
        super().__init__(f"{query}\n  The module created above command incorrectly, got error:\n    {trc.format_exc().splitlines()[-1]}")


        
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
class contains:
    def __init__(self,value):
        self.value = value
class case_insensitive:
    def __init__(self,value):
        self.value = value
class is_not:
    def __init__(self,value):
        self.value = value
class sqliteObj:
    def __init__(self,filename,table=None):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        self.conn.row_factory = sqlite3.Row
        if table == None:
            self.table = None
        else:
            self.table = self.set_table(table)
        cols = {}
        e_cols = {}
        for x in self.tables():
            t_cols = []
            te_cols = []
            for y in self.column_names(table=x):
                t_cols.append(y.lower())
                te_cols.append(y)
            cols[x] = t_cols
            e_cols[x] = te_cols
        self.col_names = cols
        self.col_names_exact = e_cols
        self.total_changes = 0


    def col_exists(self,col_name,table):
        if col_name.lower() not in self.col_names[table]:
            raise ColumnNotFound(col_name,table)
        return True

    def col_names_update(self):
        cols = {}
        for x in self.tables():
            t_cols = []
            for y in self.column_names(table=x):
                t_cols.append(y.lower())
            cols[x] = t_cols
        self.col_names = cols



    def select_all_custom(self,key,dict_mode=True,table=None,limit=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
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
        query = f'SELECT * FROM "{table}"'
        if limit != None:
            if str(type(limit)) != "<class 'int'>":
                raise Exception("'limit' must be an integer")
            else:
                query = f'{query} LIMIT {limit};'
        else:
            query = f'{query};'
        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None
        rows = cur.fetchall()

        r_rows = []
        if dict_mode:
            for x in rows:
                r = dict(x)
                kr = key(r)
                if str(type(kr)) != "<class 'bool'>":
                    raise InvalidKeyResponse(kr,key)
                else:
                    if kr:
                        r_rows.append(r)
            nRows = newRows
        else:
            for r in rows:
                kr = key(r)
                if str(type(kr)) != "<class 'bool'>":
                    raise InvalidKeyResponse(kr,key)
                else:
                    if kr:
                        r_rows.append(r)
        return r_rows

    def select_custom(self,key,select,orderDict=None,op_and=True,limit=None,case_insensitive=False,dict_mode=True,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table
        if str(type(select)) == "<class 'str'>":
            query = select
        else:
            if str(type(select)) != "<class 'dict'>":
                raise Exception("'select' must be either a dictionary or a query string")
            query = f'SELECT * FROM "{table}" WHERE'
            c = 0
            if op_and:
                op = "AND"
            else:
                op = "OR"
            for x in select:
                self.col_exists(x,table)
                if case_insensitive:
                    c_i = True
                else:
                    c_i = False
                c += 1
                item = select[x]
                nStr = ''
                if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                    item = item.value
                    c_i = True
                if str(type(item)) in ["<class '__main__.is_not'>","<class 'sqliteObj.is_not'>"]:
                    nStr = 'NOT '
                    item = item.value
                    if not c_i:
                        if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                            item = item.value
                            c_i = True
                if str(type(item)) == "<class 'str'>":
                    item = f'"{item}"'
                    newItem = f'{nStr}"{x}" = {item}'
                elif str(type(item)) == "<class 'NoneType'>":
                    item = f'NULL'
                    newItem = f'{nStr}"{x}" is {item}'
                elif str(type(item)) == "<class 'list'>":
                    itemLen = len(item)
                    newItem = f'{nStr}"{x}" IN ('
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
                    if c_i:
                        c_i = False
                elif str(type(item)) in ["<class '__main__.between'>","<class 'sqliteObj.between'>"]:
                    if nStr.startswith("NOT "):
                        newItem = f'{item.value1} > "{x}" OR {item.value2} < "{x}"'
                    else:
                        newItem = f'{nStr}"{x}" BETWEEN {item.value1} AND {item.value2}'
                elif str(type(item)) in ["<class '__main__.contains'>","<class 'sqliteObj.contains'>"]:
                    if not c_i:
                        if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                            item = item.value
                            c_i = True
                    newItem = f'{nStr}"{x}" LIKE "%{item.value}%"'
                elif str(type(item)) in ["<class '__main__.like'>","<class 'sqliteObj.like'>"]:
                    if not c_i:
                        if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                            item = item.value
                            c_i = True
                    newItem = f'{nStr}"{x}" LIKE "{item.value}"'
                else:
                    newItem = f'{nStr}"{x}" = {item}'
                if c_i:
                    newItem = f'{newItem} COLLATE NOCASE'


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
        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None
        rows = cur.fetchall()
        
        r_rows = []
        if dict_mode:
            for x in rows:
                r = dict(x)
                kr = key(r)
                if str(type(kr)) != "<class 'bool'>":
                    raise InvalidKeyResponse(kr,key)
                else:
                    if kr:
                        r_rows.append(r)
            nRows = newRows
        else:
            for r in rows:
                kr = key(r)
                if str(type(kr)) != "<class 'bool'>":
                    raise InvalidKeyResponse(kr,key)
                else:
                    if kr:
                        r_rows.append(r)
        return r_rows


        

    def select_all(self,dict_mode=True,table=None,limit=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
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
        query = f'SELECT * FROM "{table}"'
        if limit != None:
            if str(type(limit)) != "<class 'int'>":
                raise Exception("'limit' must be an integer")
            else:
                query = f'{query} LIMIT {limit};'
        else:
            query = f'{query};'
        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None
        rows = cur.fetchall()

        if dict_mode:
            newRows = []
            for x in rows:
                newRows.append(dict(x))
            return newRows
        else:
            return rows

    def select(self,select,orderDict=None,op_and=True,limit=None,case_insensitive=False,dict_mode=True,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table
        if str(type(select)) == "<class 'str'>":
            query = select
        else:
            if str(type(select)) != "<class 'dict'>":
                raise Exception("'select' must be either a dictionary or a query string")
            query = f'SELECT * FROM "{table}" WHERE'
            c = 0
            if op_and:
                op = "AND"
            else:
                op = "OR"
            for x in select:
                self.col_exists(x,table)
                if case_insensitive:
                    c_i = True
                else:
                    c_i = False
                c += 1
                item = select[x]
                nStr = ''
                if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                    item = item.value
                    c_i = True
                if str(type(item)) in ["<class '__main__.is_not'>","<class 'sqliteObj.is_not'>"]:
                    nStr = 'NOT '
                    item = item.value
                    if not c_i:
                        if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                            item = item.value
                            c_i = True
                if str(type(item)) == "<class 'str'>":
                    item = f'"{item}"'
                    newItem = f'{nStr}"{x}" = {item}'
                elif str(type(item)) == "<class 'NoneType'>":
                    item = f'NULL'
                    newItem = f'{nStr}"{x}" is {item}'
                elif str(type(item)) == "<class 'list'>":
                    itemLen = len(item)
                    newItem = f'{nStr}"{x}" IN ('
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
                    if c_i:
                        c_i = False
                elif str(type(item)) in ["<class '__main__.between'>","<class 'sqliteObj.between'>"]:
                    if nStr.startswith("NOT "):
                        newItem = f'{item.value2} > "{x}" OR {item.value1} < "{x}"'
                    else:
                        newItem = f'{nStr}"{x}" BETWEEN {item.value1} AND {item.value2}'
                elif str(type(item)) in ["<class '__main__.contains'>","<class 'sqliteObj.contains'>"]:
                    if not c_i:
                        if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                            item = item.value
                            c_i = True
                    newItem = f'{nStr}"{x}" LIKE "%{item.value}%"'
                elif str(type(item)) in ["<class '__main__.like'>","<class 'sqliteObj.like'>"]:
                    if not c_i:
                        if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                            item = item.value
                            c_i = True
                    newItem = f'{nStr}"{x}" LIKE "{item.value}"'
                else:
                    newItem = f'{nStr}"{x}" = {item}'
                if c_i:
                    newItem = f'{newItem} COLLATE NOCASE'


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
        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None
        rows = cur.fetchall()
        
        if dict_mode:
            newRows = []
            for x in rows:
                newRows.append(dict(x))
            return newRows
        else:
            return rows

    def set_table(self,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
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
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        tableList = []
        if tables != []:
            for x in tables:
                for y in x:
                    tableList.append(y)
        return tableList
    
###################################################
    
    def update(self,update,where,op_and=True,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")


        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table
                

        updateQuery = 'SET'
        uC = 0
        updateLen = len(update)
        for x in update:
            self.col_exists(x,table)
            uC += 1
            newUItem = update[x]
            if str(type(newUItem)) == "<class 'str'>":
                newUItem = f'"{newUItem}"'
            elif str(type(newUItem)) == "<class 'NoneType'>":
                newUItem = f'NULL'
            if uC == updateLen:
                updateQuery = f'{updateQuery} "{x}" = {newUItem}'
            else:
                updateQuery = f'{updateQuery} "{x}" = {newUItem},'

    
        if str(type(where)) == "<class 'str'>":
            whereQuery = f' {where}'
        else:
            if str(type(where)) == "<class 'NoneType'>" or where == {}:
                whereQuery = " "
            else:
                if str(type(where)) != "<class 'dict'>":
                    raise TypeError("'where' must be either a dictionary or a query string")
                whereQuery = ' WHERE'
                c = 0
                if op_and:
                    op = "AND"
                else:
                    op = "OR"
                for x in where:
                    self.col_exists(x,table)
                    c_i = False
                    c += 1
                    item = where[x]
                    nStr = ''
                    if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                        item = item.value
                        c_i = True
                    if str(type(item)) in ["<class '__main__.is_not'>","<class 'sqliteObj.is_not'>"]:
                        nStr = 'NOT '
                        item = item.value
                        if not c_i:
                            if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                                item = item.value
                                c_i = True
                    if str(type(item)) == "<class 'str'>":
                        item = f'"{item}"'
                        newItem = f'{nStr}"{x}" = {item}'
                    elif str(type(item)) == "<class 'NoneType'>":
                        item = f'NULL'
                        newItem = f'{nStr}"{x}" is {item}'
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
                    elif str(type(item)) in ["<class '__main__.contains'>","<class 'sqliteObj.contains'>"]:
                        if not c_i:
                            if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                                item = item.value
                                c_i = True
                        newItem = f'{nStr}"{x}" LIKE "%{item.value}%"'
                    elif str(type(item)) in ["<class '__main__.like'>","<class 'sqliteObj.like'>"]:
                        if not c_i:
                            if str(type(item)) in ["<class '__main__.case_insensitive'>","<class 'sqliteObj.case_insensitive'>"]:
                                item = item.value
                                c_i = True
                        newItem = f'{nStr}"{x}" LIKE "{item.value}"'
                    else:
                        newItem = f'{nStr}"{x}" = {item}'
                    if c_i:
                        newItem = f'{newItem} COLLATE NOCASE'


                    if c == 1:
                        whereQuery = f'{whereQuery} {newItem}'
                    else:
                        whereQuery = f'{whereQuery} {op} {newItem}'

        query = f'UPDATE "{table}" {updateQuery}{whereQuery}'
        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None
        rc = cur.rowcount
        self.total_changes += rc
        return rc
        
    
    def insert(self,insert,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        
        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table

        columns = '('
        iCount = 0
        iLen = len(insert)
        for x in insert:
            self.col_exists(x,table)
            iCount += 1
            if insert[x] == None:
                iLen -= 1
                iCount -= 1
                continue
            if iLen == iCount:
                columns = f'{columns}"{x}")'
            else:
                columns = f'{columns}"{x}", '
                
        if not columns.endswith(")"):
            if columns.endswith(", "):
                columns = f'{columns[0:-2]})'
            else:  
                columns = f'{columns})'
            

        values = '('
        iCount = 0
        for x in insert:
            if insert[x] == None:
                continue
            iCount += 1
            x = itemStr(insert[x])
            if iLen == iCount:
                values = f'{values}{x})'
            else:
                values = f'{values}{x}, '
                
        if not values.endswith(")"):
            if values.endswith(", "):
                values = f'{values[0:-2]})'
            else:  
                values = f'{values})'

        query = f'INSERT INTO "{table}" {columns} VALUES {values};'

        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None
        self.total_changes += 1

    def column_names(self,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        
        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table

        query = f'PRAGMA table_info("{table}");'

        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None

        rows = cur.fetchall()

        cols = []
        for x in rows:
            cols.append(x[1])
        return cols

    def add_column(self,column,datatype,current=None,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        
        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table

        if str(type(datatype)) == "<class 'str'>":
            datatype = TypeStr(datatype)
            
        query = f'ALTER TABLE "{table}" ADD COLUMN "{column}" {datatype.type};'
        
        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None

        self.col_names[table].append(column.lower())

        if current != None:
            cur.execute(f'UPDATE "{table}" SET "{column}" = {itemStr(current)};')
            self.total_changes += cur.rowcount        

    def drop_column(self,column,table=None):
        raise Exception("This doesnt actually work, I was dumb.")
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        
        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table

        if str(type(datatype)) == "<class 'str'>":
            datatype = TypeStr(datatype)
            
        query = f'ALTER TABLE "{table}" DROP COLUMN {column};'

        cur.execute(query)

    def create_table(self,table):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        query = f'CREATE TABLE "{table}" (id INTEGER NOT NULL, PRIMARY KEY(id AUTOINCREMENT));'
        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None
        if self.table == None:
            self.table = table
        self.col_names_update()

    def drop_table(self,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        
        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table

        query = f'DROP TABLE {table};'
        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None

    def delete(self,delete,op_and=True,table=None):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        if table == None:
            if self.table == None:
                raise TableNotSet()
            else:
                table = self.table
                
        if str(type(delete)) == "<class 'str'>":
            query = delete
        else:
            if str(type(delete)) != "<class 'dict'>":
                raise Exception("'delete' must be either a dictionary or a query string")
            query = f'DELETE FROM "{table}" WHERE'
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
                elif str(type(item)) == "<class 'NoneType'>":
                    item = f'NULL'
                    newItem = f'{nStr}"{x}" is {item}'
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

        try:
            cur.execute(query)
        except:
            raise ModuleOperationError(query,traceback) from None
        rc = cur.rowcount
        self.total_changes += rc
        return rc
        
###################################################

    def commit(self):
        self.conn.commit()

    def cursor(self):
        try:
            cur = self.conn.cursor()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                self.close()
                self.conn = sqlite3.connect(self.filename)
                self.conn.row_factory = sqlite3.Row
                cur = self.conn.cursor()
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")
        return cur

    def execute(self,query):
        cur = self.conn.cursor()
        a = cur.execute(query)
        self.total_changes += cur.rowcount
        return a

    def close(self):
        try:
            cur = self.conn.close()
        except:
            if str(sys.exc_info()[0]) == "<class 'sqlite3.ProgrammingError'>":
                None
            else:
                raise Exception(f"Unknown: {sys.exc_info()}")

