from rest_framework import serializers

from api.models import TestRunRequest, TestFilePath, TestEnvironment


class TestRunRequestSerializer(serializers.ModelSerializer):
    env_name = serializers.ReadOnlyField(source='env.name')
    file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = TestRunRequest
        fields = (
            'id',
            'requested_by',
            'env',
            'path',
            'status',
            'created_at',
            'env_name',
            'logs',
            'file'
        )
        read_only_fields = (
            'id',
            'created_at',
            'status',
            'logs',
            'env_name'
        )

    def validate_file(self, value):
        """
        Check that the uploaded file is a Python file (.py).
        """
        if not value.name.endswith('.py'):
            raise serializers.ValidationError("Only Python files are allowed.")
        return value

    def create(self, validated_data):
        file = validated_data.pop('file', None)
        try:
            test_run_request = super().create(validated_data)  # Create first
            if file:
                # Now save the file and associate
                file_path = default_storage.save(f'uploads/{file.name}', ContentFile(file.read()))
                test_file_path = TestFilePath.objects.create(path=file_path)
                test_run_request.path.add(test_file_path)
                test_run_request.save()
            return test_run_request
        except Exception as e:
            logger.error(f"Error creating TestRunRequest: {e}")
            raise serializers.ValidationError("Error saving the test run request.")


class TestRunRequestItemSerializer(serializers.ModelSerializer):
    env_name = serializers.ReadOnlyField(source='env.name')

    class Meta:
        model = TestRunRequest
        fields = (
            'id',
            'requested_by',
            'env',
            'path',
            'status',
            'created_at',
            'env_name',
            'logs'
        )


class TestFilePathSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFilePath
        fields = ('id', 'path')


class TestEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestEnvironment
        fields = ('id', 'name')
