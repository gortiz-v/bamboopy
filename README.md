# BambooHR Python Library
----

This library eases the use of the BambooHR REST API. It is an unofficial Python API for BambooHR.

This library require two additional libraries (xmltodic, rfc6266) to handle some special requests.

To use this library you can do

```python
from bamboopy import Employees

employees = Employees(
    api_key='MYCOMPANYAPIKEY',
    company='companyname')

employees = employees.directory()

```
This will give you a list of employees

You can also upload files to BambooHR

```python
from bamboopy import Employees

employees = Employees(
    api_key='MYCOMPANYAPIKEY',
    company='companyname')


employees.upload_file(
    123,
    category=12,
    file='./Contract_template.pdf',
    filename="Contract.pdf")
```