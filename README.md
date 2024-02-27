# PandaQ-SQL-interpreter-in-Python-
This project implements an interpreter for a subset of SQL queries. To consult table information, files in `csv` format will be used. In addition, the interface has been made with the Streamlit library. At the code level, the treatment of the tables has been carried out thanks to the Python Pandas library.

## Code execution

To execute this code, it will be necessary to have the grammar `pandaQ.g4` and the file `pandaQ.py` in the same folder. In a linux terminal, the following commands will be executed:

```bash
antlr4 -Dlanguage=Python3 -no-listener -visitor pandaQ.g4
streamlit run pandaQ.py
```
Regarding the tables from which information can be consulted, they must be in the same folder as the grammar and the code in Python and in `csv` format.

## Usage

Below will be mentioned the various inquiries that can be made and various clarifications about them, when necessary. It should be noted that in the Query box you can only make a query, which will return a table. If we want to do more, we will delete what we have put and write the new query.

### Select all rows of a table
```bash
select * from table;
```
With this format, all the rows of a table can be consulted, as long as there is a .csv file in the same folder or a previously declared variable (more information later) with the name of this table.

### Select certain fields from a table
```bash
select field1, field2... from table;
```
With this format you can consult certain fields of a table. In addition, these fields can be calculated as in the following example:
```bash
select field_not_calculated, field_not_calculated*2 as field_calculated from table;
```
We can assign various expressions with basic arithmetic operations to a new field. The following symbols (), +, -, *, / can appear in these expressions. Multiplication and division take precedence over addition and subtraction. Additionally, multiple fields, even calculated fields, can appear in expressions, as long as they appear after they have been declared in the query.

### Where functionality
This functionality allows you to declare a boolean expression in order to apply a filter to the rows, so that only those columns that pass the filter will be displayed. The format is as follows:
```bash
select fields from table where condition;
```
The following symbols <, =, and, not, () can be used in the condition. The < and = operations will be between two fields or between a field and an integer (and vice versa). Unselected fields can be written to the condition, if they are part of the table initially.

### Odrer functionality by
Another of the implemented functionalities is the order by, which allows the rows to be displayed based on various fields in ascending or descending order with the following format:
```bash
select fields from table order by field1 [asc|desc], field2 [asc|desc];
```
If ascending or descending is not specified, it will be assumed to be ascending. In addition, fields that have not been selected can be specified, as long as they are part of the table to be consulted. It should be said that the order by must always be declared after the where, in case there is a where.
### Inner join functionality
Allows you to make several inner joins of the table to be selected with other tables, indicating by which field we match one to the other. The format is as follows:
```bash
select fields from table1
inner join table2 where
       field_table_1 = field_table_2;
```
When we select the fields, we can indicate fields that are not originally from table1, if they are part of a table with which table1 will be joined. As mentioned, several inner joins can be chained one after the other.
It should be noted that if two fields match in name between two tables that do an inner join (without being the field in which they match), the name of the two fields will be changed by adding a suffix to each of them to differentiate them. In this way, between two matching fields, the suffixes will be _x and _y.
### Table of symbols
We can save in a variable with a certain name a query. This variable will work from this moment on as another table with which we can work. We observe the following format:
```bash
id := query;
select * from id;
```
Please note that these are separate inquiries. They will have to be done one after the other, not in the same box at the same time.
A conflict may occur between variable names and tables in `csv` format. To solve this, variable names will take precedence. That is, if they match, the table saved in the variable will be taken.
### Plot
Allows you to graph numerical data from a table saved to a variable in the following format:
```bash
plot id;
```
It should be noted that the table may contain non-numeric fields, but these will not be shown in the plot.

### Subqueries
Subqueries can be made in the following format:
```bash
select fields from table where field in (query);
```
This also implies that the subquery can have another subquery, this one another, and so on. That is, several levels of subquery.

## Commented code

It is necessary to clarify that all functions in the Python code are commented in order to understand what is done in each of them.

## Author

Sergi Pérez
