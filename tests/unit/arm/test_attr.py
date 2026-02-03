import pytest

from payload.arm.attr import (
    Attr,
    Contains,
    Equal,
    Filter,
    GreaterThan,
    GreaterThanEqual,
    LessThan,
    LessThanEqual,
    NotEqual,
)


class TestFilterOr:
    """Unit tests for Filter.__or__ method"""

    @pytest.mark.parametrize(
        'filter1, filter2, expected_attr, expected_opval',
        [
            # Same filter types
            (
                Equal('status', 'active'),
                Equal('status', 'pending'),
                'status',
                'active|pending',
            ),
            (
                NotEqual('status', 'inactive'),
                NotEqual('status', 'deleted'),
                'status',
                '!inactive|!deleted',
            ),
            (
                GreaterThan('score', '50'),
                GreaterThan('score', '75'),
                'score',
                '>50|>75',
            ),
            (
                LessThan('price', '100'),
                LessThan('price', '50'),
                'price',
                '<100|<50',
            ),
            (
                GreaterThanEqual('age', '18'),
                GreaterThanEqual('age', '21'),
                'age',
                '>=18|>=21',
            ),
            (
                LessThanEqual('discount', '20'),
                LessThanEqual('discount', '10'),
                'discount',
                '<=20|<=10',
            ),
            (
                Contains('name', 'john'),
                Contains('name', 'jane'),
                'name',
                '?*john|?*jane',
            ),
            # Mixed filter types
            (
                Equal('amount', '100'),
                GreaterThan('amount', '200'),
                'amount',
                '100|>200',
            ),
            # Filters from Attr objects
            (
                Attr.status == 'active',
                Attr.status == 'pending',
                'status',
                'active|pending',
            ),
        ],
        ids=[
            'equal_filters',
            'notequal_filters',
            'greaterthan_filters',
            'lessthan_filters',
            'greaterthanequal_filters',
            'lessthanequal_filters',
            'contains_filters',
            'mixed_filter_types',
            'attr_object_filters',
        ],
    )
    def test_filter_or_success_cases(self, filter1, filter2, expected_attr, expected_opval):
        """Test OR operation with various filter types on the same attribute"""
        result = filter1 | filter2

        assert isinstance(result, Equal)
        assert result.attr == expected_attr
        assert result.opval == expected_opval
        assert result.val == expected_opval

    @pytest.mark.parametrize(
        'other_value, expected_error_msg',
        [
            ('not_a_filter', 'invalid type'),
            (None, 'invalid type'),
            ({'status': 'pending'}, 'invalid type'),
            (30, 'invalid type'),
        ],
        ids=['string', 'none', 'dict', 'int'],
    )
    def test_filter_or_with_invalid_types_raises_typeerror(
        self, other_value, expected_error_msg
    ):
        """Test that OR operation with non-Filter types raises TypeError"""
        filter1 = Equal('status', 'active')

        with pytest.raises(TypeError) as exc_info:
            filter1 | other_value

        assert str(exc_info.value) == expected_error_msg

    def test_filter_or_different_attributes_raises_valueerror(self):
        """Test that OR operation on different attributes raises ValueError"""
        filter1 = Equal('status', 'active')
        filter2 = Equal('name', 'john')

        with pytest.raises(ValueError) as exc_info:
            filter1 | filter2

        assert str(exc_info.value) == '`or` only works on the same attribute'

    def test_filter_or_chained_operations(self):
        """Test OR operation chained multiple times"""
        filter1 = Equal('color', 'red')
        filter2 = Equal('color', 'blue')
        filter3 = Equal('color', 'green')

        result = filter1 | filter2 | filter3

        assert isinstance(result, Equal)
        assert result.attr == 'color'
        assert result.opval == 'red|blue|green'

    @pytest.mark.parametrize(
        'filter1, filter2, expected_attr, expected_opval',
        [
            # Preserves existing pipes in values
            (
                Equal('status', 'active|pending'),
                Equal('status', 'approved'),
                'status',
                'active|pending|approved',
            ),
            # Nested attribute paths
            (
                Equal('user[address][city]', 'NYC'),
                Equal('user[address][city]', 'LA'),
                'user[address][city]',
                'NYC|LA',
            ),
            # Numeric string values
            (
                Equal('id', '123'),
                Equal('id', '456'),
                'id',
                '123|456',
            ),
            # Empty string values
            (
                Equal('description', ''),
                Equal('description', 'test'),
                'description',
                '|test',
            ),
        ],
        ids=[
            'preserves_pipes',
            'nested_attributes',
            'numeric_strings',
            'empty_string',
        ],
    )
    def test_filter_or_edge_cases(self, filter1, filter2, expected_attr, expected_opval):
        """Test OR operation with edge cases"""
        result = filter1 | filter2

        assert isinstance(result, Equal)
        assert result.attr == expected_attr
        assert result.opval == expected_opval

    def test_filter_or_symmetry(self):
        """Test that OR operation works in both directions"""
        filter1 = Equal('status', 'active')
        filter2 = Equal('status', 'pending')

        result1 = filter1 | filter2
        result2 = filter2 | filter1

        # Results should have the same components (though order may differ)
        assert result1.attr == result2.attr
        assert set(result1.opval.split('|')) == set(result2.opval.split('|'))
