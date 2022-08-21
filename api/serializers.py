from re import S
from rest_framework import serializers
from api.models import Tweet
from drf_writable_nested.serializers import WritableNestedModelSerializer, NestedUpdateMixin

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields=('url', 'tweet')

# class EntitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Entity
#         fields = ['name', 'user_name', 'screen_name', 'profile_image']

# class PointSerializer(WritableNestedModelSerializer):
#     author = EntitySerializer()

#     class Meta:
#         model = Point
#         fields = ['author', 'text']

#     # def create(self, validated_data):
#     #     author_data = validated_data.pop('author')
#     #     author_model = Entity.objects.create(**author_data)
#     #     point = Point.objects.create(author=author_model, **validated_data)
        
#     #     return point

# class SectionSerializer(WritableNestedModelSerializer):
#     points = PointSerializer(many=True)

#     class Meta:
#         model = Section
#         fields = ['points']

#     # def create(self, validated_data):
#     #     points_data = validated_data.pop('points')
#     #     points_model = Point.objects.create(**points_data)
#     #     section = Point.objects.create(author=points_model, **validated_data)
        
#     #     return section


# class TweetSerializer(WritableNestedModelSerializer):

#     sections = SectionSerializer(many=True)
#     author = EntitySerializer()
#     publisher = EntitySerializer()

#     class Meta:
#         model = Tweet
#         fields = ['url', 'title', 'subtitle', 'time', 'publisher', 'author', 'image', 'sections']
    
#     # def create(self, validated_data):
        
#     #     author_data = validated_data.pop('author')
#     #     sections_data = validated_data.pop('sections')
#     #     publisher_data = validated_data.pop('publisher')
#     #     sections_model = []
#     #     for section in sections_data:
#     #         sections = Section.objects.create(**section)
#     #         sections_model.append(sections)
#     #     author_model = Entity.objects.create(**author_data)
#     #     publisher_model = Entity.objects.create(**publisher_data)
#     #     tweet = Point.objects.create(author=author_model, publisher=publisher_model, sections=sections_model, **validated_data)
        
#     #     return tweet