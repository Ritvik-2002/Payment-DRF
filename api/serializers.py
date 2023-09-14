from rest_framework import serializers
import datetime

from api.models import CreditCard, Payment, Order, EBT

class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = [
            "id",
            "number",
            "last_4",
            "brand",
            "exp_month",
            "exp_year",
        ]

    #last_4 should be same as number last 4 digits
    def validate(self, data):
        number = data.get('number')
        last_4 = data.get('last_4')
        if number and last_4 and number[-4:] != last_4:
            raise serializers.ValidationError("Last 4 digits of card number should be same as last_4 field.")
        
        # check if card is expired
        exp_month = data.get('exp_month')
        exp_year = data.get('exp_year')
        if exp_month and exp_year:
            current_year = datetime.datetime.now().year%100
            current_month = datetime.datetime.now().month
            if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
                raise serializers.ValidationError("Card is expired.")
            
            return data    


class EBTSerializer(serializers.ModelSerializer):
    class Meta:
        model = EBT
        fields = [
            "id",
            "number",
            "last_4",
            "state",
            "issue_month",
            "issue_year",
        ]

    #last_4 should be same as number last 4 digits
    def validate(self, data):
        number = data.get('number')
        last_4 = data.get('last_4')
        if number and last_4 and number[-4:] != last_4:
            raise serializers.ValidationError("Last 4 digits of ebt number should be same as last_4 field.")
            
        return data      


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "order_total",
            "status",
            "success_date",
            "ebt_total",
        ]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order", # The id of the associated Order object
            "amount",
            "description",
            "credit_card", # The id of the associated CreditCard object
            "ebt", # The id of the associated EBT object
            "payment_method", # The id of the associated CreditCard object
            "status",
            "success_date",
            "last_processing_error"
        ]

    def validate(self, data):
        payment_method = data.get('payment_method')
        credit_card = data.get('credit_card')
        ebt = data.get('ebt')

        if payment_method == 'credit_card' and not credit_card:
            raise serializers.ValidationError("You must select a Credit Card payment method.")
        elif payment_method == 'ebt' and not ebt:
            raise serializers.ValidationError("You must select an EBT payment method.")

        # Ensure only one payment method is selected
        if credit_card and ebt:
            raise serializers.ValidationError("You can't select both Credit Card and EBT as active payment methods.")
        
        # check snap total now  is less than order total
        order = data.get('order')
        amount = data.get('amount')
        if order and amount:
            order_obj = Order.objects.get(id=order.id)
            total_payment_amount = sum([x.amount for x in Payment.objects.filter(order__id=order.id)])
            if total_payment_amount + amount > order_obj.order_total:
                raise serializers.ValidationError("Payment total exceeds order total for Order with id {}".format(order.id))
                
        return data    

    
