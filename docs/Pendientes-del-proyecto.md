# Pendientes del proyecto Coworkhub

## Estado actual

La aplicación ya cuenta con:

- Registro e inicio de sesión de usuarios.
- Persistencia de usuarios en la base de datos.
- Cierre de sesión.
- Dashboard y perfil de usuario.
- Reservas de espacios y salas.
- Sedes y salas iniciales.
- Pagos simulados por reserva.
- Planes y suscripciones simuladas.
- Permisos especiales para `admin@demo.com`.
- Microservicio Flask para cotizaciones.
- Docker Compose con Django, Flask y Nginx.
- Pruebas automatizadas.
- Documentación del Strangler Pattern.
- PostgreSQL y Redis/Celery configurados para Docker Compose.
- Integración local con servicio aliado y Adapter para API de terceros.
- Soporte inicial de idiomas español e inglés con `gettext`.
- Notificaciones persistidas generadas por tareas Celery.
- Auditoría UX/UI de los flujos principales.

## Prioridad alta

### Entrega 2 - requisitos locales completados

- [x] Extraer cotizaciones a Flask y enrutar con Nginx.
- [x] Añadir PostgreSQL y Redis al entorno Docker Compose.
- [x] Añadir worker Celery para confirmaciones asíncronas.
- [x] Exponer y consumir un servicio aliado de demostración.
- [x] Implementar Adapter para API de terceros.
- [x] Configurar i18n español/inglés con gettext.
- [x] Consumir una API pública mediante Adapter.
- [x] Persistir evidencia de tareas asíncronas.
- [x] Documentar auditoría UX/UI.
- [ ] Desplegar en AWS Academy (paso manual del estudiante).
- [ ] Consumir el servicio real de un equipo aliado.

### 1. Integrar una pasarela de pagos real

- [ ] Elegir proveedor: Wompi, PayU, Stripe o Mercado Pago.
- [ ] Reemplazar la aprobación automática de pagos.
- [ ] Manejar pagos aprobados, rechazados y pendientes.
- [ ] Implementar webhooks para confirmar transacciones.
- [ ] Implementar reembolsos.

> **Entorno académico simulado:** para demostrar pagos aprobados en el
> proyecto usa la tarjeta ficticia `4242 4242 4242 4242`, vencimiento `12/30`
> y código CVV `123`. No se realizan cobros ni se almacenan datos de tarjeta.

### 2. Completar las suscripciones

- [x] Controlar las horas disponibles por plan.
- [x] Validar el máximo de reservas activas.
- [x] Implementar renovación automática.
- [x] Permitir cancelar una suscripción.
- [x] Actualizar automáticamente suscripciones vencidas.
- [x] Mostrar el estado y consumo de cada suscripción.

### 3. Completar la gestión de reservas

- [ ] Permitir cancelar reservas.
- [ ] Permitir editar reservas.
- [ ] Mostrar el historial completo de reservas.
- [ ] Validar horarios de apertura y cierre de cada sede.
- [ ] Mostrar disponibilidad en tiempo real.
- [ ] Enviar confirmaciones de reserva.

### 4. Crear un panel administrativo completo

- [x] Administrar usuarios.
- [x] Administrar sedes.
- [x] Administrar salas y espacios.
- [x] Consultar todas las reservas.
- [x] Administrar planes y suscripciones.
- [x] Revisar pagos y facturas.
- [x] Crear roles adicionales: administrador, operador y usuario.

### 5. Preparar la seguridad para producción

- [ ] Mover `SECRET_KEY` a variables de entorno.
- [ ] Desactivar `DEBUG` en producción.
- [ ] Configurar `ALLOWED_HOSTS` correctamente.
- [ ] Configurar HTTPS y certificados TLS.
- [ ] Proteger credenciales y archivos `.env`.
- [ ] Configurar políticas de contraseñas.
- [ ] Agregar rate limiting en Nginx.

## Prioridad media

### 6. Mejorar la interfaz de usuario

- [ ] Mostrar mensajes de error más claros.
- [ ] Completar la adaptación responsive.
- [ ] Agregar estados de carga.
- [ ] Mostrar el costo antes de confirmar una reserva.
- [ ] Mejorar la selección visual de sedes y salas.
- [ ] Agregar filtros por ciudad, capacidad y disponibilidad.

### 7. Ampliar las pruebas

- [ ] Probar pagos rechazados.
- [ ] Probar pagos pendientes.
- [ ] Probar reembolsos.
- [ ] Probar cancelación de reservas.
- [ ] Probar suscripciones vencidas.
- [ ] Probar permisos administrativos.
- [ ] Probar integración entre Django, Flask, Nginx y Docker.
- [ ] Agregar pruebas de carga.

### 8. Mejorar observabilidad

- [ ] Implementar logs estructurados.
- [ ] Centralizar errores.
- [ ] Agregar health checks para Django y Flask.
- [ ] Registrar tiempos de respuesta.
- [ ] Crear métricas de reservas y pagos.
- [ ] Configurar alertas ante fallos.

### 9. Preparar la base de datos

- [ ] Migrar de SQLite a PostgreSQL para producción.
- [ ] Configurar respaldos automáticos.
- [ ] Definir estrategia de recuperación ante fallos.
- [ ] Agregar índices para consultas de reservas y fechas.
- [ ] Revisar políticas de retención de datos.

## Prioridad de entrega profesional

### 10. Automatización y despliegue

- [ ] Crear un pipeline CI/CD con GitHub Actions.
- [ ] Ejecutar automáticamente pruebas en cada Pull Request.
- [ ] Separar ambientes de desarrollo, pruebas y producción.
- [ ] Automatizar migraciones durante el despliegue.
- [ ] Configurar versionado de imágenes Docker.
- [ ] Documentar el proceso de rollback.

### 11. Documentación

- [ ] Crear manual de instalación.
- [ ] Crear manual de usuario.
- [ ] Documentar todos los endpoints.
- [ ] Documentar variables de entorno.
- [ ] Actualizar los diagramas de arquitectura.
- [ ] Agregar capturas de pantalla de los flujos principales.
- [ ] Mantener actualizada la Wiki de GitHub.

## Orden recomendado de trabajo

1. Integrar pagos reales.
2. Completar suscripciones y límites de uso.
3. Completar cancelación y disponibilidad de reservas.
4. Crear el panel administrativo.
5. Migrar a PostgreSQL y reforzar seguridad.
6. Ampliar pruebas y observabilidad.
7. Automatizar despliegues.
8. Finalizar manuales y documentación.

## Criterio de aplicación lista para producción

La aplicación podrá considerarse lista para producción cuando:

- Los pagos reales estén confirmados mediante webhooks.
- Las reservas validen disponibilidad y horarios correctamente.
- Las suscripciones controlen límites y vencimientos.
- Exista un panel administrativo completo.
- La aplicación use HTTPS y secretos externos.
- La base de datos tenga respaldos.
- Las pruebas cubran los flujos críticos.
- Existan logs, métricas y alertas.
- El despliegue sea reproducible mediante CI/CD.
