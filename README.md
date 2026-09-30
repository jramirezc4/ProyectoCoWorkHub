# Coworkhub

API para la gestion de un coworking: usuarios, sedes, espacios, reservas,
finanzas y opiniones. Esta entrega implementa el flujo principal de reservas
con Django REST Framework y una separacion explicita entre presentacion,
aplicacion y dominio.

## Ejecucion local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/api/reservas/`. Requiere
autenticacion. Para la demostracion se puede usar la sesion del admin o Basic
Authentication con un usuario creado desde `/admin/`.

## Endpoints

| Metodo | URL | Resultado |
|---|---|---|
| GET | `/api/reservas/` | Reservas del usuario autenticado |
| POST | `/api/reservas/` | Crea y confirma una reserva |
| GET | `/api/reservas/<id>/` | Consulta una reserva propia |

Ejemplo de entrada:

```json
{
	"espacio_id": 1,
	"fecha_inicio": "2026-09-01T09:00:00Z",
	"fecha_fin": "2026-09-01T11:00:00Z",
	"modalidad_pago": "PAGO_USO"
}
```

Respuestas relevantes: `201` creacion exitosa, `400` datos invalidos,
`404` reserva inexistente o ajena, y `409` conflicto de disponibilidad o
suscripcion.

## Arquitectura y responsabilidades

- `reservas/api_views.py`: recibe HTTP, autentica, invoca el servicio y
	transforma excepciones en codigos HTTP. No calcula precios ni disponibilidad.
- `reservas/serializers.py`: valida forma, tipos, choices y serializa la
	respuesta. No contiene reglas de negocio.
- `reservas/services.py`: caso de uso `ReservationService`; valida
	suscripcion y solapamiento, solicita el calculador al Factory y persiste la
	reserva dentro de una transaccion.
- `reservas/domain/reservation_builder.py`: construye la entidad compleja de
	reserva paso a paso y verifica campos obligatorios/fechas.
- `reservas/infra/factories.py`: Factory selecciona calculador real o mock por
	`COWORKHUB_COST_CALCULATOR`, aislando la variante de calculo.
- `reservas/models.py`, `finanzas/models.py`, `usuarios/models.py` y
	`opiniones/models.py`: entidades persistentes del avance del dominio.
- `opiniones/services.py`: operaciones de publicar, editar y eliminar reseñas;
	las reglas de aplicación no viven en el modelo.

Esta distribucion aplica SRP: cada capa tiene una razon de cambio distinta y
la vista depende del servicio, no de detalles de calculo o persistencia.

## Secuencia de creacion de reserva

```mermaid
sequenceDiagram
		actor Cliente
		participant API as ReservationCollectionAPIView
		participant In as ReservationCreateSerializer
		participant Service as ReservationService
		participant Factory as ReservationCostCalculatorFactory
		participant Builder as ReservationBuilder
		participant DB as Base de datos

		Cliente->>API: POST datos de reserva
		API->>In: validar payload
		In-->>API: datos tipados
		API->>Service: create_reservation(usuario, datos)
		Service->>DB: comprobar suscripcion y solapamientos
		Service->>Factory: create()
		Factory-->>Service: calculador real/mock
		Service->>Builder: construir entidad
		Builder-->>Service: Reserva validada
		Service->>DB: guardar reserva confirmada
		DB-->>Service: reserva persistida
		Service-->>API: reserva
		API-->>Cliente: 201 + ReservationSerializer
```

## Preparacion para API Gateway

El Gateway puede enrutar `/api/reservas/*` al servicio HTTP de reservas y
mantener ocultos los modulos internos. La autenticacion, rate limiting,
tracing y CORS pueden centralizarse en el Gateway, mientras Django conserva
autorizacion a nivel de recurso: cada usuario solo consulta sus reservas.
La API usa JSON, codigos HTTP estandar y una URL versionable (`/api/v1/` en
una siguiente iteracion), por lo que puede escalar horizontalmente detras del
Gateway. La logica de aplicacion no depende del servidor web y el Factory
permite sustituir el calculador por una integracion externa sin cambiar la
vista.

## Patrones creacionales

- **Builder:** evita un constructor con muchos parametros para `Reserva` y
	centraliza la construccion valida de la entidad.
- **Factory:** encapsula la seleccion entre calculador real y mock. Para usar
	el mock en pruebas o una demo: `COWORKHUB_COST_CALCULATOR=MOCK`.

## Migracion a microservicios

La cotizacion de reservas fue extraida a un microservicio Flask independiente.
Django conserva usuarios, disponibilidad, suscripciones y persistencia; Flask
calcula el costo a traves de `POST /api/v2/cotizaciones/` y responde JSON.

Para levantar la topologia completa con Nginx:

```powershell
docker compose up --build
```

La documentacion de la matriz de decision, el diagrama y la separacion tecnica
esta en [docs/Migracion-a-Microservicios.md](docs/Migracion-a-Microservicios.md).