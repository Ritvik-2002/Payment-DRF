# See the fixtures/ directory for examples of the request bodies
# needed to create objects using the ListCreateAPIViews below.

from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import Payment, CreditCard, Order, EBT
from api.serializers import PaymentSerializer, CreditCardSerializer, OrderSerializer, EBTSerializer
from processor import processPayment

class ListCreateCreditCard(ListCreateAPIView):
    """ Exposes the following routes,
    
    1. GET http://localhost:8000/api/credit_cards/ <- returns a list of all CreditCard objects
    2. POST http://localhost:8000/api/credit_cards/ <- creates a single CreditCard object and returns it

    """
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer

    def get(self,request):
        credit_cards = CreditCard.objects.all()
        serializer = CreditCardSerializer(credit_cards, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = CreditCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class RetrieveDeleteCreditCard(RetrieveDestroyAPIView):
    """ Exposes the following routes,
    
    1. GET http://localhost:8000/api/credit_cards/:id/ <- returns a CreditCard object provided its id.
    2. DELETE http://localhost:8000/api/credit_cards/:id/ <- deletes a CreditCard object by id.

    """
    queryset = CreditCard.objects.all()
    serializer_class = CreditCardSerializer

    def get(self,request,pk):
        credit_card = CreditCard.objects.get(pk=pk)
        serializer = CreditCardSerializer(credit_card, many=False)
        return Response(serializer.data)
    
    def delete(self,request,pk):
        credit_card = CreditCard.objects.get(id=pk)
        credit_card.delete()
        return Response("Credit Card Deleted")

class ListCreateEBT(ListCreateAPIView):
    """ Exposes the following routes,
    
    1. GET http://localhost:8000/api/ebt/ <- returns a list of all EBT objects
    2. POST http://localhost:8000/api/ebt/ <- creates a single EBT object and returns it

    """
    queryset = EBT.objects.all()
    serializer_class = EBTSerializer

    def get(self,request):
        ebts = EBT.objects.all()
        serializer = EBTSerializer(ebts, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = EBTSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
class RetrieveDeleteEBT(RetrieveDestroyAPIView):
    """ Exposes the following routes,
    
    1. GET http://localhost:8000/api/ebt/:id/ <- returns a EBT object provided its id.
    2. DELETE http://localhost:8000/api/ebt/:id/ <- deletes a EBT object by id.

    """
    queryset = EBT.objects.all()
    serializer_class = EBTSerializer

    def get(self,request,pk):
        ebt = EBT.objects.get(pk=pk)
        serializer = EBTSerializer(ebt, many=False)
        return Response(serializer.data)
    
    def delete(self,request,pk):
        ebt = EBT.objects.get(id=pk)
        ebt.delete()
        return Response("EBT Deleted")


class ListCreateOrder(ListCreateAPIView):
    """ Exposes the following routes,
    
    1. GET http://localhost:8000/api/orders/ <- returns a list of all Order objects
    2. POST http://localhost:8000/api/ordersr/ <- creates a single Order object and returns it

    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self,request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class RetrieveDeleteOrder(RetrieveDestroyAPIView):
    """ Exposes the following routes,
    
    1. GET http://localhost:8000/api/orders/:id/ <- returns an Order object provided its id.
    2. DELETE http://localhost:8000/api/orders/:id/ <- deletes an Order object by id.

    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self,request,pk):
        order = Order.objects.get(pk=pk)
        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)
    
    def delete(self,request,pk):
        order = Order.objects.get(id=pk)
        order.delete()
        return Response("Order Deleted")


class ListCreatePayment(ListCreateAPIView):
    """ Exposes the following routes,
    
    1. GET http://localhost:8000/api/payments/ <- returns a list of all Payment objects
    2. POST http://localhost:8000/api/payments/ <- creates a single Payment object and associates it with the Order in the request body.

    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get(self,request):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = PaymentSerializer(data=request.data)
        # check snap total less than order total
        # order_id = request.data['order']
        # order = Order.objects.get(id=order_id)
        # amount = Decimal(request.data['amount'])
        # if order.order_total < amount:
        #     return Response("Payment amount exceeds order total")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    


class RetrieveDeletePayment(RetrieveDestroyAPIView):
    """ Exposes the following routes,
    
    1. GET http://localhost:8000/api/payments/:id/ <- returns a Payment object provided its id.
    2. DELETE http://localhost:8000/api/payments/:id/ <- deletes a Payment object by id.

    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get(self,request,pk):
        payment = Payment.objects.get(pk=pk)
        serializer = PaymentSerializer(payment, many=False)
        return Response(serializer.data)
    
    def delete(self,request,pk):
        payment = Payment.objects.get(pk=pk)
        payment.delete()
        return Response("Payment Deleted")
    


class CaptureOrder(APIView):
    """ Provided an Order's id, submit all associated payments to the payment processor.

    Payments will change status to either failed or succeeded, depending on the
    response from the payment processor.

    Once all payments have been processed, the status of the Order object will be updated
    to 'suceeded' if all of the payments were successful or 'failed' if at least one payment
    was not successful.
    """

    def get(self, request, id):
        payment_queryset = Payment.objects.filter(order__id=id)
        serializer = PaymentSerializer(payment_queryset, many=True)
        return Response(serializer.data)



    def post(self, request, id):
        try:
            order_obj = Order.objects.get(id=id) # throws if order_id not found

            # Find all Payments associated with this Order via /api/payments/
            payment_queryset = Payment.objects.filter(order__id=id)

            # Payments must satisfy the order_total
            total_payment_amount = sum([x.amount for x in payment_queryset])
            if total_payment_amount != order_obj.order_total:
                order_obj.status = Order.TYPE_FAILED
                order_obj.save()
                for payment in payment_queryset:
                    payment.status = Payment.TYPE_FAILED
                    payment.last_processing_error = "Payment total does not match order total for Order with id {}".format(id)
                    payment.save()
                return Response({
                    "error_message": "Payment total does not match order total for Order with id {}".format(id)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Payment related to EBT must satisfy the ebt_total
            total_ebt_amount = sum([x.amount for x in payment_queryset if x.payment_method == "ebt"])
            if total_ebt_amount > order_obj.ebt_total:
                order_obj.status = Order.TYPE_FAILED
                order_obj.save()
                for payment in payment_queryset:
                    payment.status = Payment.TYPE_FAILED
                    payment.last_processing_error = "EBT total exceeded order ebt total for Order with id {}".format(id)
                    payment.save()
                return Response({
                    "error_message": "EBT total exceeded order ebt total for Order with id {}".format(id)
                }, status=status.HTTP_400_BAD_REQUEST,)
            
            potential_errors = []
            for payment in payment_queryset:
                potential_error = processPayment(payment)

                if potential_error:
                    potential_errors.append(potential_error)

            if potential_errors:
                order_obj.status = Order.TYPE_FAILED
            else:
                order_obj.status = Order.TYPE_SUCCEEDED
                order_obj.success_date = timezone.now()

            order_obj.save() # write status back to database

            return Response(
                OrderSerializer(order_obj).data
            )

        except Order.DoesNotExist:
            return Response({
                "error_message": "Unable to find Order with id {}".format(id)
            }, status=status.HTTP_404_NOT_FOUND)
