from rest_framework import serializers
from auths.models import CustomUser
from .models import UserProfile
import os
from django.core.files.base import ContentFile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'address',
            'date_of_birth',
            'gender',
            'city',
            'country',
            'postal_code',
            'bio',
            'website',
            'facebook',
            'linkedin',
            'twitter',
            'company',
            'job_title'
        ]

    

class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'full_name',
            'phone',
            'image',
            'profile'
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        image = validated_data.pop('image', None)

        instance.email = validated_data.get('email', instance.email)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone = validated_data.get('phone', instance.phone)

        # Handle image upload: delete old image and save new with user_id as filename
        if image:
            # delete old image if it exists
            if instance.image:
                try:
                    instance.image.delete(save=False)
                except Exception:
                    pass

            # get file extension from the uploaded image
            original_name = image.name
            ext = os.path.splitext(original_name)[1]  # e.g., '.png', '.jpg'
            
            # create new filename with user_id
            new_filename = f"profile/{instance.id}{ext}"
            
            # save image with new filename
            instance.image.save(new_filename, image, save=False)

        instance.save()

        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance



