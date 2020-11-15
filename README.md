
[![A](https://auxilus.ml/resources/auxilus_thin)](https://auxilus.ml)

If you have any questions, suggestions, or comments, message me on Discord at Pmblue#1085. I am happy to address anything that I can. I would also love any feedback, because as I said, I am a hobby programmer, and have no formal education in programming. Thank you for your time.

It may help to note that some commands and code in there, such as the clear command, were copy/pasted from my previous projects, and I still am planning on largely changing/redoing many things like that to better fit the bot, be more optimized, ect. There are quite a few things I know I need to change/redo, though telling me anything you see still cant hurt, because I would not be surprised if I am missing something even after my testing. 



I am frankly inexperienced in SQL, and prefer OOP where possible. To make it easier on myself, and as a fun side project, I made this module. Hope that you find them helpful, and if not, at least I can use them when I forget it myself.
# __**sqliteObj Documentation**__
## sqliteObj(*filename*,table=None)
Initializes and connects to the database that is specified in *filename*. The *table* argument is the same as using the *set_table()* method. All of the below items are methods of this object.
  **total_changes**
  Simple attribute, showing the total amount of changes to rows via this db object, using update, insert, delete methods.

**select_all(*dict_mode=True*,*table=None*,*limit=None*)**
This returns a list with all of the rows in the table. By default, they are returned as dictionaries, with the keys being the names of the columns. But if you set `dict_mode` to False, they will return as tuples. Table would be a string with the name of the table you want to query, but when initializing the special sqlite object I made, you can set a default table there anyway, so that if it is set to None it just uses that default. Limit attribute would be an integer to limit results to a certain amount of rows.

**select(*select*,*orderDict=None*,*op_and=True*,*limit=None*,*case_insensitive=False*,*dict_mode=True*,*table=None*)**
The `select` variable is a dictionary of filters for the query, or a string with an. The keys are the column names, and the values would be the filter/thing you are looking for in that column. You can put values into a list, to check if the column is equal to any of them. There are a few classes that you can put values in to set certain options:
*between(value1,value2)* - Checks if column is between or equal to those numbers.
*like(value)* - Checks value based on formatted string you provide. See https://www.tutorialspoint.com/sql/sql-like-clause.htm to see formatting and examples.
*is_not(value)* - Its just a not operator. You can put normal values, lists, between, like, and other such values in here. Ex: `{"id": is_not(between(1,5)),"column_name": is_not(contains("hello"))}`
*contains(value)* - Check if a columns's value contains the provided value.
*case_insensitive(value)* - Make search case insensitive. Much like is_not, various other valid objects can be placed in here, to make their search case insensitive. If case_insensitive argument is set to True, then this class is irrelevant. Ex: `{"id": case_insensitive(is_not(between(1,5)))}`

 `op_and` makes it so that it adds `AND` for the operator. This means that a row must meet ALL of the criteria within the query. If this is turned off, it uses the `OR` operator instead, meaning that the rows only need to meet ONE of the criteria. `limit` can be set to an integer, to limit the amount of results. `orderDict` can be a dictionary, which would determine how the results are ordered. The keys would be set to column names, and the values would be either 1 or 0. 1 is for descending and 0 is for ascending order. If case_insensitive is True, then all searches will be case insensitive. 

**tables()**
Returns a list of the names of the available tables in the database.

**set_table(*table=None*)**
Used to set the default table if it was not done upon initialization of the object. If table is left equal to None, than it will set the default to the first table found, if any. This basically makes it so that anywhere in this documentation you see *table=None* as an argument, it is automatically filled with the set table if left as None.

**update(*update*,*where*,*op_and=True*,*table=None*)**
Updates the selected rows on the table. The *where* dictionary essentially works in the same way as the *select* dictionary works in the select() method listed above, and the same with *table* and *op_and*. If None or an empty dictionary are provided for *where*, it will update all rows. This method will return an integer, with the amount of rows updated.
*update* - This is a dictionary where the keys are the columns you want to update, and the values are what you want those columns to be set to. These changes are only made to columns selected with the *where* dictionary.

**insert(*insert*,*table=None*)**
This inserts a row into a table. *insert* is a dictionary, where the keys are the column names, and the values are going to be the values inserted into the columns for that row. Any columns that are not defined, will be NULL.

**add_column(*column*,*datatype*,*current=None*,*table=None*)**
Creates a new column in a table. The *column* argument determines the name of the new column, and *datatype* determines the type. The following is a list of datatype objects:
- **Integer()**: Integer data type for sql
- **Real()**: Real data type for sql. Allows for float number values.
- **Text()**: Text data type for sql. Used for storing strings.
- **TypeStr(*value*)**: Custom data type. If you want to use another datatype for the column that is available with sqlite, then you would enter it as a string for *value*. If you provide a string for the *datatype* argument instead of one of the first three objects, this object is automatically used instead.

The *current* variable is only used if you want to set a value for the new column to be used in all existing rows, rather than NULL. If left as None, then all of the rows in the column will be NULL.

**drop_column(*column*,*table=None*)**
*Just a heads up, I am an actual idiot. This doesnt work, you cant just drop a column super ez unfortunately. Dont use this.*
Drops (removes) a column from a table with the name given.

**create_table(*table*)**
Create a new table named *table*. If a table was not set with the *set_table()* method or upon object initialization, then the default table becomes this table. A column called *id* is automatically used in the table, as an Integer datatype, that auto increments and is set as the primary key.

**drop_table(*table=None*)**
Drops (removes) the table selected, or whatever table is set as the default.

**commit()**
Commits (writes/saves) all changes you have made to the database, such as new columns, new rows, deleted rows, ect.

**execute(*query*)**
Want to send a raw sql command? That is what this function is for. Insert a string with the sql command.

**cursor()**
Get a sqlite3 cursor object for this database.

**delete(*delete*,*op_and=True*,*table=None*)**
Deletes all of the rows selected using the params provided in the *delete* dictionary. *delete* and *op_and* work same as in *select* method, with *delete* arg being the equivilent of the *select* methods' *select* argument. This method will return an integer, with the amount of rows deleted. 

***
### Custom Selections
**select_all_custom(*key*,*dict_mode=True*,*table=None*,*limit=None*)**
This returns a list with all of the rows in the table. By default, they are returned as dictionaries, with the keys being the names of the columns. But if you set `dict_mode` to False, they will return as tuples. Table would be a string with the name of the table you want to query, but when initializing the special sqlite object I made, you can set a default table there anyway, so that if it is set to None it just uses that default. Limit attribute would be an integer to limit results to a certain amount of rows.
