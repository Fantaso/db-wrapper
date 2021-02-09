import datetime
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
class BaseFieldFormat:
    # TODO: change dict to tuple
    TYPE = None
    ALLOW_LOOKUPS = (
        "gt",
        "lt",
        "gte",
        "lte",
        "in",
        "not_in",
    )

    LOOKUPS = {
        None: ("=", "equal_str"),
        "gt": (">", "gt_str"),
        "lt": ("<", "lt_str"),
        "gte": (">=", "gte_str"),
        "lte": ("<=", "lte_str"),
        "in": ("IN", "in_str"),
        "not_in": ("NOT IN", "not_in_str"),
    }

    def __init__(self, raw_field: str, raw_value: Union[str, int, datetime.date, List]):
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
            supported_lookups = ",".join(lup for lup in self.LOOKUPS.keys() if lup is not None)
            raise FilterLookupError(f"This lookup is not supported: try {supported_lookups}")

    def is_lookup_query(self, field: str):
        return True if "__" in field else False

    def split_field_and_lookup(self, raw_field):
        field, lookup = raw_field.split("__")
        return field, lookup

    ### All fields ###
    def equal_str(self, lookup) -> str:
        return self.format_str_condition(lookup)

    ### Numeric, Date fields ###
    def gt_str(self, lookup) -> str:
        return self.format_str_condition(lookup)

    def lt_str(self, lookup) -> str:
        return self.format_str_condition(lookup)

    def gte_str(self, lookup) -> str:
        return self.format_str_condition(lookup)

    def lte_str(self, lookup) -> str:
        return self.format_str_condition(lookup)

    def format_str_condition(self, lookup):
        return f"{self.field}{lookup}{self.get_formatted_single_value(self.value)}"

    def get_formatted_single_value(self, value) -> str:
        """
        Override this method to change how the value in the condition if formatted.
        e.g:
        field = name   =>  if field(column) in database is a string type: return a string type: 'name'
        field = 7   =>  if field(column) in database is a integer type: return a string type: str(7)
        field = datetime.date(2021,2,2)   =>  if field(column) in database is a date type: return a string type formatted: strftime('%Y-%m-%d')
        """
        return f"'{value}'"

    ### Lists[all fields] ###
    def in_str(self, lookup) -> str:
        return self.format_list_condition(lookup)

    def not_in_str(self, lookup) -> str:
        return self.format_list_condition(lookup)

    def format_list_condition(self, lookup):
        return f"{self.field} {lookup} ({self.get_formatted_value_in_list(self.value)})"

    # utils
    def get_formatted_value_in_list(self, values: List) -> str:
        """
        Override this method to change how the values in the list are formatted to create the final condition.
        e.g:
        field in [name1, name2, ]   =>
            if field(column) in database is a string type: return a string type concatenated: 'name1','name2'
        field in [3, 7, ]   =>
            if field(column) in database is a integer type: return a string type concatenated: str(3),str(7)
        field in [datetime.date(2021,2,2), ]   =>
            if field(column) in database is a date type: return a string type concatenated and formatted:
            strftime('%Y-%m-%d'),strftime('%Y-%m-%d')
        """
        format = lambda x: f"'{x}'"
        return ','.join(list(map(format, values)))


#######################
###  FIELD CLASSES  ###
#######################
class StringFieldFormat(BaseFieldFormat):
    TYPE = str
    ALLOW_LOOKUPS = ("in", "not_in")


class DateFieldFormat(BaseFieldFormat):
    TYPE = datetime.date

    def get_formatted_single_value(self, value) -> str:
        """ Overriding the format of the date value condition. """
        return f"'{value.strftime('%Y-%m-%d')}'"

    def get_formatted_value_in_list(self, values: List) -> str:
        """ Overriding the format of the date values in the list. """
        format_date = lambda x: f"'{x.strftime('%Y-%m-%d')}'"  # explicitly instead of __str__()
        return ','.join(list(map(format_date, self.value)))


class IntegerFieldFormat(BaseFieldFormat):
    TYPE = int

    def get_formatted_single_value(self, value) -> str:
        """ Overriding the format of the integer value condition. """
        return f"{value}"

    def get_formatted_value_in_list(self, values: List) -> str:
        """ Overriding the format of the integer values in the list. """
        format = lambda x: f"{x}"
        return ','.join(list(map(format, values)))


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
        elif isinstance(self.raw_value, datetime.date):
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
