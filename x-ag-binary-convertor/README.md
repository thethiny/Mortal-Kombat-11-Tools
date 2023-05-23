Deserialize.py contains python implementation of save file conversion & x-ag-binary conversion
xag_json.cpp contains the c++ implementation of the x-ag-binary format only for those used in MK11, so it is missing some stuff
ag_conv.py can convert json to x-ag

## x-ag-binary format

| Data Type            | Binary Format | Data Size                  |
|----------------------|---------------|----------------------------|
| zero                 | 00             | 1 byte                     |
| null                 | 01            | 1 byte                     |
| true                 | 02            | 1 byte                     |
| false                | 03            | 1 byte                     |
| sint8                | 10            | 1 byte                     |
| int8                 | 11            | 1 byte                     |
| sint16               | 12            | 2 bytes                    |
| int16                | 13            | 2 bytes                    |
| sint32               | 14            | 4 bytes                    |
| int32                | 15            | 4 bytes                    |
| sint64               | 16            | 8 bytes                    |
| int64                | 17            | 8 bytes                    |
| float                | 20            | 4 bytes                    |
| double?              | 21            | 8? bytes                   |
| string               | 30            | 1 byte length + string     |
| string               | 31            | 2 bytes length + string    |
| string               | 32            | 4 bytes length + string    |
| binary data, size 1  | 33            | 1 byte length + data       |
| binary data, size 2  | 34            | 2 bytes length + data      |
| binary data, size 4  | 35            | 4 bytes length + data      |
| long long int, size 8| 36            | 8 bytes                    |
| epoch time           | 40            | 8 bytes                    |
| List `[`             | 50            | 1 byte items count         |
| List `[`             | 51            | 2 bytes items count        |
| List `[`             | 52            | 4 bytes items count        |
| List `[`             | 53            | 8 bytes items count        |
| Dictionary `{`       | 60            | 1 byte items count         |
| Dictionary `{`       | 61            | 2 bytes items count        |
| Dictionary `{`       | 62            | 4 bytes items count        |
| Dictionary `{`       | 63            | 8 bytes items count        |

