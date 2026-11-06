# Auditoría UX/UI - Entrega 2

## Flujos revisados

| Flujo | Resultado |
|---|---|
| Registro e inicio de sesión | Formularios con validación y mensajes de error. |
| Creación de reserva | Espacio, fechas, modalidad y pago demo en un solo flujo. |
| Disponibilidad | Se rechazan solapamientos, horarios inválidos y sedes inactivas. |
| Suscripción | Se muestran planes, límites, consumo, tarjeta demo y factura. |
| Cancelación | Reserva y suscripción usan acciones POST protegidas por CSRF. |
| Reseña | Solo se puede reseñar una reserva completada propia. |
| Administración | Django Admin centraliza usuarios, roles, reservas y pagos. |
| Espacios disponibles | `/espacios/` muestra salas disponibles, hora local y clima por sede. |

## Criterios de usabilidad

- Los formularios muestran etiquetas, ayudas y errores junto al campo.
- Las vistas privadas requieren autenticación.
- La navegación incluye inicio, dashboard, perfil, reservas y planes.
- Las plantillas incluyen viewport responsive y rejillas adaptables.
- Los mensajes de éxito y error se muestran después de las operaciones.
- El selector de idioma permite cambiar entre español e inglés.

## Evidencia para sustentación

1. Crear una cuenta y acceder al dashboard.
2. Crear una reserva usando la tarjeta demo.
3. Mostrar la factura y notificación generadas.
4. Abrir `/espacios/` para consultar disponibilidad, hora local y clima.
5. Ejecutar `docker compose ps` para mostrar servicios saludables.
