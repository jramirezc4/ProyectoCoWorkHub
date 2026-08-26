from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reservas.serializers import ReservationCreateSerializer, ReservationSerializer
from reservas.services import (
    ReservationConflictError,
    ReservationService,
    SubscriptionRequiredError,
)
from reservas.models import Reserva


class ReservationCollectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reservations = request.user.reservas.select_related('espacio__sede').order_by('-fecha_creacion')
        return Response(ReservationSerializer(reservations, many=True).data)

    def post(self, request):
        input_serializer = ReservationCreateSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = ReservationService().create_reservation(
                usuario=request.user,
                **input_serializer.validated_data,
            )
        except SubscriptionRequiredError as error:
            return Response({'detail': error.message}, status=status.HTTP_409_CONFLICT)
        except ReservationConflictError as error:
            return Response({'detail': error.message}, status=status.HTTP_409_CONFLICT)
        except ValidationError as error:
            return Response({'detail': error.messages}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)


class ReservationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        reservation = get_object_or_404(
            Reserva.objects.select_related('espacio__sede', 'usuario'),
            pk=pk,
            usuario=request.user,
        )
        return Response(ReservationSerializer(reservation).data)