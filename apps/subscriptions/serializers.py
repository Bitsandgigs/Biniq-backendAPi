from datetime import datetime
from rest_framework import serializers
from django.utils import timezone
from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'type', 'tier', 'amount', 'duration']
        read_only_fields = ['id']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        exclude = ['card_number', 'cvc']
        read_only_fields = ['id', 'order_id', 'user', 'user_name', 'amount', 'status', 'date', 'duration']


class SubscriptionCreateSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=[('tier1','tier1'),('tier2','tier2'),('tier3','tier3')])
    payment_method = serializers.DictField()

    def validate(self, attrs):
        pm = attrs.get('payment_method') or {}
        required = ['card_number', 'cardholder_name', 'expiry_month', 'expiry_year', 'cvc']
        missing = [k for k in required if not pm.get(k)]
        if missing:
            raise serializers.ValidationError({'payment_method': f"Missing fields: {', '.join(missing)}"})
        if not isinstance(pm.get('card_number'), str) or len(pm['card_number']) != 16 or not pm['card_number'].isdigit():
            raise serializers.ValidationError({'payment_method.card_number': 'Card number must be 16 digits'})
        if not isinstance(pm.get('expiry_month'), str) or pm['expiry_month'] not in [f"{i:02d}" for i in range(1,13)]:
            raise serializers.ValidationError({'payment_method.expiry_month': 'Valid expiry month (01-12) is required'})
        if not isinstance(pm.get('expiry_year'), str) or not pm['expiry_year'].isdigit() or len(pm['expiry_year']) != 4:
            raise serializers.ValidationError({'payment_method.expiry_year': 'Valid expiry year is required'})
        if not isinstance(pm.get('cvc'), str) or not (3 <= len(pm['cvc']) <= 4) or not pm['cvc'].isdigit():
            raise serializers.ValidationError({'payment_method.cvc': 'Valid CVC (3-4 digits) is required'})
        return attrs
