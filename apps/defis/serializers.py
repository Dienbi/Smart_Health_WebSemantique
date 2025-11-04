from rest_framework import serializers
from .models import (
    Defi, DefiObjectif, DefiBadge, DefiStatus,
    Participation, ParticipationProgress, ParticipationNumber, ParticipationRange
)


class DefiObjectifSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefiObjectif
        fields = '__all__'


class DefiBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefiBadge
        fields = '__all__'


class DefiStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefiStatus
        fields = '__all__'


class DefiSerializer(serializers.ModelSerializer):
    objectives = DefiObjectifSerializer(many=True, read_only=True)
    badge = DefiBadgeSerializer(read_only=True)
    status = DefiStatusSerializer(read_only=True)
    participation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Defi
        fields = '__all__'
        read_only_fields = ('defi_id',)
    
    def get_participation_count(self, obj):
        return obj.participations.count()


class ParticipationProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipationProgress
        fields = '__all__'


class ParticipationNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipationNumber
        fields = '__all__'


class ParticipationRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipationRange
        fields = '__all__'


class ParticipationSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    defi_name = serializers.CharField(source='defi.defi_name', read_only=True)
    progress = ParticipationProgressSerializer(read_only=True)
    number = ParticipationNumberSerializer(read_only=True)
    range = ParticipationRangeSerializer(read_only=True)
    
    class Meta:
        model = Participation
        fields = '__all__'
        read_only_fields = ('participation_id',)
