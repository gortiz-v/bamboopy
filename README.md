# BambooHR Python Library
----

This library eases the use of the BambooHR REST API. It is an unofficial Python API for BambooHR.

This library require two additional libraries (xmltodic, rfc6266) to handle some special requests.

To use this library you can do

```python
from bamboopy import SingleDimensionalData

ssd = SingleDimensionalData(
    api_key='MYCOMPANYAPIKEY',
    company='companyname',
)

employees = ssd.get_directory()

```
This will give you a list of employees

You can also upload files to BambooHR

```python
from bamboopy import SingleDimensionalData

ssd = SingleDimensionalData(
    api_key='MYCOMPANYAPIKEY',
    company='companyname',
)

ssd.upload_employee_file(
    123,
    category=12,
    file='./Contract_template.pdf',
    filename="Contract.pdf")
```