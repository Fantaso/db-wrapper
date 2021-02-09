from abc import ABCMeta, abstractmethod
from datetime import date
from typing import List, Union


####################
###  EXCEPTIONS  ###
####################
class FilterLookupError(LookupError):
    """ When a developer is filtering by a lookup not supported in sql API. """


class FieldTypeNotSupportedError(Exception):
    """ When a developer filters the database with an unsupported field type."""


######################
###  BASE CLASSES  ###
######################
class BaseSingleFieldFormat:
    def get_format_condition(self, lookup_operator):
        return f"{self.field}{lookup_operator}{self.get_format_value()}"

    def get_format_value(self) -> str:
        """
        Method that calls the subclass which holds the final format of the value to be used on the sql condition..
        e.g:
        field = name   =>  if field(column) in database is a string type: return a string type: 'name'
        field = 7   =>  if field(column) in database is a integer type: return a string type: str(7)
        field = datetime.date(2021,2,2)   =>  if field(column) in database is a date type: return a string type formatted: strftime('%Y-%m-%d')
        """
        return self.format_value(self.value)


class BaseListFieldFormat:
    def get_format_list_condition(self, lookup_operator):
        return f"{self.field} {lookup_operator} ({self.get_format_list_value()})"

    def get_format_list_value(self) -> str:
        """
        Method that calls the subclass which holds the final format of the value to be used on the sql condition.
        e.g:
        field in [name1, name2, ]   =>
            if field(column) in database is a string type: return a string type concatenated: 'name1','name2'
        field in [3, 7, ]   =>
            if field(column) in database is a integer type: return a string type concatenated: str(3),str(7)
        field in [datetime.date(2021,2,2), ]   =>
            if field(column) in database is a date type: return a string type concatenated and formatted:
            strftime('%Y-%m-%d'),strftime('%Y-%m-%d')
        """
        return ','.join(list(map(self.format_value, self.value)))


class BaseFieldFormat(BaseSingleFieldFormat, BaseListFieldFormat, metaclass=ABCMeta):
    TYPE = None
    ALLOW_LOOKUPS = (
        "gt",
        "lt",
        "gte",
        "lte",
        "in",
        "not_in",
    )

    # TODO: change dict to tuple
    LOOKUPS = {
        None: ("=", "get_format_condition"),
        "gt": (">", "get_format_condition"),
        "lt": ("<", "get_format_condition"),
        "gte": (">=", "get_format_condition"),
        "lte": ("<=", "get_format_condition"),
        "in": ("IN", "get_format_list_condition"),
        "not_in": ("NOT IN", "get_format_list_condition"),
    }

    def __init__(self, raw_field: str, raw_value: Union[str, int, date, List]):
        self.raw_field = raw_field
        self.raw_value = raw_value
        self.field = None
        self.value = None
        self.lookup = None

    ### Main
    def get_string(self) -> str:
        self.field, self.value = self.raw_field, self.raw_value
        if self.is_lookup_query(self.field):
            self.field, self.lookup = self.split_field_and_lookup(self.field)
            self.validate_lookup()
            sql_lookup, str_func = self.LOOKUPS[self.lookup]
        else:
            # instead of None. Better way?
            sql_lookup, str_func = self.LOOKUPS[None]

        sql_str = getattr(self, str_func)(sql_lookup)
        return sql_str

    # utils
    def validate_lookup(self):
        if self.lookup not in self.ALLOW_LOOKUPS:
            supported_lookups = ", ".join(lup for lup in self.LOOKUPS.keys() if lup is not None)
            raise FilterLookupError(f"This lookup is not supported: try {supported_lookups}")

    def is_lookup_query(self, field: str):
        return True if "__" in field else False

    def split_field_and_lookup(self, raw_field):
        field, lookup = raw_field.split("__")
        return field, lookup

    @abstractmethod
    def format_value(self, value: TYPE) -> str:
        """
        Override this method to change how the value in the condition if formatted.
        e.g:
        field = name   =>  if field(column) in database is a string type: return a string type: 'name'
        field = 7   =>  if field(column) in database is a integer type: return a string type: str(7)
        field = datetime.date(2021,2,2)   =>  if field(column) in database is a date type: return a string type formatted: strftime('%Y-%m-%d')
        """


#######################
###  FIELD CLASSES  ###
#######################
class StringFieldFormat(BaseFieldFormat):
    TYPE = str
    ALLOW_LOOKUPS = ("in", "not_in")

    def format_value(self, value: str) -> str:
        """
        This will return sql condition formatted for a string value:
        - for a single value => field='value' or for all operators in class attr ALLOW_LOOKUPS
        - for a value list => field IN ('value1', 'value2', )
        """
        return f"'{value}'"


class DateFieldFormat(BaseFieldFormat):
    TYPE = date

    def format_value(self, value: date) -> str:
        """
        This will return sql condition formatted for an date value:
        - for a single value => field='%Y-%m-%d' or field>='%Y-%m-%d' or for all operators in class attr ALLOW_LOOKUPS
        - for a value list => field (NOT) IN ('%Y-%m-%d', '%Y-%m-%d', )
        """
        return f"'{value.strftime('%Y-%m-%d')}'"


class IntegerFieldFormat(BaseFieldFormat):
    TYPE = int

    def format_value(self, value: int) -> str:
        """
        This will return sql condition formatted for an integer value:
        - for a single value => field='%Y-%m-%d' or field>='%Y-%m-%d' or for all operators in class attr ALLOW_LOOKUPS
        - for a value list => field (NOT) IN (value1, value2, )
        """
        return f"{value}"


###################
###  INTERFACE  ###
###################
class Format:
    FORMAT_CLASSES = (
        DateFieldFormat,
        StringFieldFormat,
        IntegerFieldFormat,
    )

    def __init__(self, raw_field, raw_value):
        self.raw_field = raw_field
        self.raw_value = raw_value

    def get_format_class(self):
        ### Basic fields
        if isinstance(self.raw_value, int):
            return IntegerFieldFormat(self.raw_field, self.raw_value)
        elif isinstance(self.raw_value, str):
            return StringFieldFormat(self.raw_field, self.raw_value)
        elif isinstance(self.raw_value, date):
            return DateFieldFormat(self.raw_field, self.raw_value)

        ### When they come in a list for lookups such: [IN, NOT IN]
        elif isinstance(self.raw_value, list):
            if not self.are_homogeneous_type(self.raw_value):
                raise ValueError("All values must be same type.")
            return self.get_class_from_type()(self.raw_field, self.raw_value)

        else:
            raise FieldTypeNotSupportedError(
                "The field type you are trying to filter upon is not supported. "
                f"{','.join([type(klass.TYPE) for klass in self.FORMAT_CLASSES])}"
            )

    ### utils: dealing with list type
    def are_homogeneous_type(self, values: List):
        _iter = iter(values)
        first_type = type(next(_iter))
        return True if all((type(x) is first_type) for x in _iter) else False

    def get_class_from_type(self):
        first_value = self.raw_value[0]
        for klass in self.FORMAT_CLASSES:
            if isinstance(first_value, klass.TYPE):
                return klass
