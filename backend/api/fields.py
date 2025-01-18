from rest_framework.serializers import IntegerField


class CustomIntegerField(IntegerField):

    def to_internal_value(self, data):
        if isinstance(data, str) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')
        return data
