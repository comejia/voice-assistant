---
include: always
---

# Conventional Commits

Siempre que te pida redactar un mensaje de commit, analizar cambios de Git (`git diff`) o preparar una confirmación en este repositorio, debés aplicar estrictamente estas reglas.

## Estructura del Mensaje
La primera línea debe seguir este formato exacto:
`tipo(alcance opcional): descripción corta`

## Tipos Permitidos y Cuándo Usarlos
- `feat`: Añadir una nueva característica o funcionalidad al código.
- `fix`: Solucionar un error (bug fix).
- `docs`: Modificaciones exclusivas en la documentación (README, comentarios).
- `style`: Cambios de formato, espacios, puntos y comas (sin alterar la lógica).
- `refactor`: Reestructuración de código que no corrige errores ni añade funciones.
- `perf`: Cambios enfocados puramente en mejorar el rendimiento del sistema.
- `test`: Adición, corrección o actualización de pruebas unitarias o de integración.
- `chore`: Tareas de mantenimiento, actualización de dependencias o configuración.

## Reglas de Formato Obligatorias
1. **Longitud:** La primera línea no debe superar los 50 caracteres.
2. **Gramática:** Usar el verbo principal en modo imperativo y en español (ej: "añadir", "corregir", "eliminar", "actualizar").
3. **Estilo:** La descripción debe comenzar en minúscula y NO debe incluir un punto final.
4. **Seguridad:** Nunca ejecutes comandos destructivos o envíos remotos (`git push`) de forma automática sin que yo te lo autorice explícitamente.