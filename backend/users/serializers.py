"""Serializers for the users app."""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser


class LoginSerializer(serializers.Serializer):
    """Validates login credentials using empleado_id + password."""
    empleado_id = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        empleado_id = attrs.get('empleado_id')
        password = attrs.get('password')

        try:
            user = CustomUser.objects.get(empleado_id=empleado_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                {'detail': 'Credenciales inválidas.'}
            )

        if user.is_blocked:
            raise serializers.ValidationError(
                {'detail': 'Tu cuenta está bloqueada. Contacta al administrador.'}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {'detail': 'Credenciales inválidas.'}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {'detail': 'Cuenta desactivada.'}
            )

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only serializer for the current user's profile."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'empleado_id', 'username', 'email',
            'first_name', 'last_name', 'full_name',
            'role', 'departamento', 'is_blocked',
            'date_joined', 'last_login',
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer for SuperAdmin user management (create/edit)."""
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'empleado_id', 'username', 'email',
            'first_name', 'last_name',
            'role', 'departamento', 'is_blocked',
            'password', 'is_active',
            'date_joined', 'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class EmployeeCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new employee and sending welcome email.
    Used by the EmployeeCreateView (SuperAdmin only).
    """
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    role = serializers.ChoiceField(
        choices=CustomUser.Role.choices,
        default=CustomUser.Role.EMPLEADO,
    )
    departamento = serializers.CharField(max_length=100, required=False, default='')

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Ya existe un usuario con este email.'
            )
        return value

    def create(self, validated_data):
        """
        Create the user. The plain password is stored temporarily
        in _plain_password for the view to use when sending the email.
        """
        plain_password = validated_data.pop('password')
        email = validated_data['email']

        # Generate empleado_id from email prefix + counter
        prefix = email.split('@')[0].upper()[:10]
        base_id = prefix
        counter = 1
        while CustomUser.objects.filter(empleado_id=base_id).exists():
            base_id = f'{prefix}{counter}'
            counter += 1

        user = CustomUser.objects.create_user(
            username=email.split('@')[0],
            email=email,
            password=plain_password,
            empleado_id=base_id,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data.get('role', CustomUser.Role.EMPLEADO),
            departamento=validated_data.get('departamento', ''),
        )
        # Attach plain password so the view can send it via email
        user._plain_password = plain_password
        return user
