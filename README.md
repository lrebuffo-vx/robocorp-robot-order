# RobotSpareBin – Pedido automático de robots

Automatización RPA en Python con [Robocorp](https://github.com/robocorp/robocorp) que carga pedidos de robots en el sitio de práctica [RobotSpareBin Industries](https://robotsparebinindustries.com/#/robot-order) y guarda un comprobante PDF de cada uno.

## Qué hace

1. **Descarga los pedidos** desde `https://robotsparebinindustries.com/orders.csv`. Cada fila trae el número de pedido, la cabeza, el cuerpo, las piernas y la dirección.
2. **Abre el sitio** y cierra el modal de aviso que aparece al entrar.
3. **Por cada pedido:**
   - Completa el formulario: cabeza (lista desplegable), cuerpo (radio button), piernas (número de pieza) y dirección.
   - Hace clic en **Preview** y después en **Order**. El sitio falla al azar al enviar el pedido, así que el robot reintenta hasta 10 veces, hasta que aparece el recibo.
   - Guarda el recibo como PDF en `receipts/receipt_<n>.pdf`.
   - Saca una captura de la vista previa del robot en `images/robot_<n>.png`.
   - Agrega esa captura como página nueva al final del PDF del recibo.
   - Hace clic en **Order another robot** y vuelve a cerrar el modal.
4. **Comprime los recibos y las imágenes** en un ZIP dentro de `archive/`.

Cada paso queda registrado con `robocorp.log`. Los mensajes se ven en `output/log.html` al terminar.

## Estructura

| Archivo | Contenido |
|---|---|
| `tasks.py` | La tarea `order_robots_from_RobotSpareBin` y las funciones de cada paso |
| `conda.yaml` | Entorno: Python 3.13, `robocorp`, `robocorp-browser` y `rpaframework` |
| `robot.yaml` | Configuración del robot para RCC / Sema4.ai |

Las librerías que usa:

- `robocorp.browser` (Playwright) para navegar, completar el formulario y sacar capturas.
- `RPA.HTTP` para descargar el CSV.
- `RPA.PDF` para convertir el recibo a PDF y agregarle la imagen.

## Cómo ejecutarlo

**Con VS Code:** instalá la extensión [Sema4.ai SDK](https://sema4.ai/docs/automation/visual-studio-code/extension-features), abrí la carpeta y ejecutá la tarea **Run Task** desde el panel lateral. La extensión arma el entorno de `conda.yaml` sola.

**Con RCC** desde la terminal:

```
rcc run
```

## Resultados

| Carpeta | Contenido |
|---|---|
| `receipts/` | Un PDF por pedido, con el recibo y la imagen del robot |
| `images/` | Las capturas de cada robot |
| `archive/` | El ZIP con los recibos y las imágenes |
| `output/` | `log.html` con el detalle de la ejecución |

Ninguna de estas carpetas se sube al repositorio (están en `.gitignore`).

## Pendiente

- `archive_receipts()` usa `PDF().create_zip_archive`, un método que `RPA.PDF` no tiene, así que el último paso falla. Hay que reemplazarlo por `RPA.Archive` (`archive_folder_with_zip`).
