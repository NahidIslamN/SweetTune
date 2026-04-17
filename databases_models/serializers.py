from rest_framework import serializers
from .models import SetupStorage, String



from rest_framework import serializers

class StringSerializer(serializers.ModelSerializer):
    class Meta:
        model = String
        fields = '__all__'
    


class SetupStorageSerializer(serializers.ModelSerializer):
    strings = StringSerializer(many=True)

    class Meta:
        model = SetupStorage
        fields = [
            "id",
            "setup_name",
            "instrument_type",
            "total_strings",
            "scale_sength",
            "is_multi_scale",
            "string_type",
            "selected_tuning",
            "total_tension",
            "strings",
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        strings_data = validated_data.pop('strings')
        setup = SetupStorage.objects.create(**validated_data)

        for string_data in strings_data:
            string = String.objects.create(**string_data)
            setup.strings.add(string)

        return setup

    def update(self, instance, validated_data):
        strings_data = validated_data.pop('strings', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if strings_data is not None:
            instance.strings.clear()

            for string_data in strings_data:
                string = String.objects.create(**string_data)
                instance.strings.add(string)

        return instance





class LegentSetupStorageSerializer(serializers.ModelSerializer):
    strings = StringSerializer(many=True)

    class Meta:
        model = SetupStorage
        fields = [
            "id",
            "setup_name",
            "instrument_type",
            "total_strings",
            "scale_sength",
            "is_multi_scale",
            "string_type",
            "selected_tuning",
            "total_tension",
            "strings",
            "is_varified",
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        strings_data = validated_data.pop('strings')
        setup = SetupStorage.objects.create(**validated_data)

        for string_data in strings_data:
            string = String.objects.create(**string_data)
            setup.strings.add(string)

        return setup

    def update(self, instance, validated_data):
        strings_data = validated_data.pop('strings', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if strings_data is not None:
            instance.strings.clear()

            for string_data in strings_data:
                string = String.objects.create(**string_data)
                instance.strings.add(string)

        return instance