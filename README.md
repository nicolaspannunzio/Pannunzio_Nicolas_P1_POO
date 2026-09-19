# Food Store - Catálogo Modular (Parcial 1 - Programación IV)

Implementación del catálogo de productos de **Food Store**, enfocada en diseño orientado a objetos en Python (encapsulamiento, contratos, relaciones estructurales y polimorfismo).

---

## Estructura del Proyecto

* `catalogo.py`: Modelo de dominio completo (clase abstracta `Producto`, subclases `ProductoSimple`, `ProductoPorPeso`, `ProductoCombo`, entidades `Categoria`, `UnidadMedida`, composición `ProductoCategoria`, wrapper `ProductoDestacado` y contrato `Exportable`).
* `libreria_externa.py`: Módulo de terceros que implementa `FichaPuntoDeVenta` (sin modificar).
* `main.py`: Script de demostración integral y validación de reglas de negocio.
* `link_video.txt`: Archivo de texto plano con el enlace al video de defensa oral.
* `uml/modelo_final.md`: Documentación del diseño y especificación del diagrama de clases en sintaxis Mermaid.

---

## Ejecución del Proyecto

El proyecto utiliza únicamente la biblioteca estándar de Python (versión 3.12 o superior), sin requerir dependencias externas ni entornos virtuales.

Para ejecutar la demostración:

```bash
python main.py
```

## Autor

**Nicolás A. Pannunzio** – Full Stack Developer & QA Specialist
🔗 [Perfil de LinkedIn](https://www.linkedin.com/in/nicolas-a-pannunzio-/)