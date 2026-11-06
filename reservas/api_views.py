from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reservas.serializers import ReservationCreateSerializer, ReservationSerializer
from reservas.services import (
    ReservationCancellationError,
    ReservationConflictError,
    ReservationService,
    SubscriptionRequiredError,
)
from reservas.models import Espacio, Reserva


class ReservationCollectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reservations = Reserva.objects.select_related('espacio__sede', 'usuario').order_by('-fecha_creacion')
        if not request.user.has_full_access():
            reservations = reservations.filter(usuario=request.user)
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
        reservation = get_object_or_404(self._queryset_for(request.user), pk=pk)
        return Response(ReservationSerializer(reservation).data)

    def delete(self, request, pk):
        reservation = get_object_or_404(self._queryset_for(request.user), pk=pk)
        try:
            ReservationService().cancel_reservation(reserva=reservation)
        except ReservationCancellationError as error:
            return Response({'detail': error.message}, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _queryset_for(user):
        reservations = Reserva.objects.select_related('espacio__sede', 'usuario')
        if not user.has_full_access():
            reservations = reservations.filter(usuario=user)
        return reservations


class ReservationAvailabilityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        espacio_id = request.query_params.get('espacio_id')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        if not all((espacio_id, fecha_inicio, fecha_fin)):
            return Response(
                {'detail': 'espacio_id, fecha_inicio y fecha_fin son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            espacio = Espacio.objects.select_related('sede').get(pk=espacio_id)
            available = ReservationService().is_available(
                espacio=espacio,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
            )
        except Espacio.DoesNotExist:
            return Response({'detail': 'El espacio no existe.'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as error:
            return Response({'detail': error.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'disponible': available})