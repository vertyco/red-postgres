from piccolo.columns import ForeignKey, Varchar
from piccolo.table import Table, sort_table_classes


class Thing(Table):
    name = Varchar(length=50)

class OtherThing(Table):
    name = Varchar(length=50)
    
TABLES = sort_table_classes([Thing, OtherThing])