# Diagrama de Clases del Modelo Final - Food Store

## Justificación del Rediseño de `ProductoDestacado` (Requerimiento 3 / HU-P1-05)

En el modelo de partida, `ProductoDestacado` aparecía heredando de `Producto`. Dicha relación fue rediseñada reemplazando la herencia por **Asociación / Envoltorio**:
1. **Criterio «es-un» violado:** Estar destacado en vidriera es un rol promocional o estado transitorio de exhibición, no una forma intrínseca de venta o tarificación como sí lo son `ProductoSimple`, `ProductoPorPeso` o `ProductoCombo`.
2. **Evitar explosión combinatoria:** Si se mantuviera la herencia, para destacar un fiambre al peso o un combo de ofertas se requeriría herencia múltiple o clases redundantes (`ProductoPorPesoDestacado`, `ProductoComboDestacado`).
3. **Solución implementada:** `ProductoDestacado` es una clase que contiene la referencia al `Producto` que destaca (`_producto: Producto`) y su orden de aparición (`_orden_vidriera: int`), permitiendo destacar de manera uniforme cualquier subclase del catálogo sin forzar la jerarquía de herencia.

---

## Diagrama de Clases (Mermaid)

```mermaid
classDiagram
    class Exportable {
        <<Protocol>>
        +exportar() str
    }

    class Producto {
        <<abstract>>
        #_nombre: str
        #_precio_base: float
        #_stock_cantidad: float
        #_habilitado: bool
        #_unidad_venta: UnidadMedida
        #_clasificaciones: list~ProductoCategoria~
        +nombre: str
        +precio_base: float
        +stock_cantidad: float
        +unidad_venta: UnidadMedida
        +disponible: bool
        +precio_publicado: str
        +precio_final(cantidad: float)* float
        +habilitar() None
        +deshabilitar() None
        +clasificar_en(categoria: Categoria, es_principal: bool) None
        +categorias() tuple~ProductoCategoria~
        +categoria_principal() Categoria
        +exportar() str
    }

    class ProductoSimple {
        +precio_final(cantidad: float) float
    }

    class ProductoPorPeso {
        +precio_final(cantidad: float) float
    }

    class ProductoCombo {
        #_componentes: list~Producto~
        #_descuento: float
        +descuento: float
        +componentes() tuple~Producto~
        +precio_final(cantidad: float) float
    }

    class ProductoDestacado {
        <<rediseñado sin herencia>>
        #_producto: Producto
        #_orden_vidriera: int
        +producto: Producto
        +orden_vidriera: int
        +exportar() str
    }

    class ProductoCategoria {
        #_categoria: Categoria
        #_es_principal: bool
        +categoria: Categoria
        +es_principal: bool
        #_marcar_principal(valor: bool) None
    }

    class Categoria {
        #_nombre: str
        #_descripcion: str
        +nombre: str
        +descripcion: str
    }

    class UnidadMedida {
        <<frozen dataclass>>
        +nombre: str
        +simbolo: str
        +tipo: str
    }

    class FichaPuntoDeVenta {
        <<libreria externa>>
        #_codigo: str
        #_detalle: str
        +exportar() str
    }

    Producto <|-- ProductoSimple : herencia
    Producto <|-- ProductoPorPeso : herencia
    Producto <|-- ProductoCombo : herencia

    Producto "1" *-- "1..*" ProductoCategoria : composicion
    ProductoCategoria "0..*" --> "1" Categoria : asociacion
    ProductoCombo "1" o-- "2..*" Producto : agregacion
    Producto "0..*" --> "0..1" UnidadMedida : asociacion

    ProductoDestacado "0..*" --> "1" Producto : asociacion / envoltorio

    Producto ..|> Exportable : conformidad estructural
    ProductoDestacado ..|> Exportable : conformidad estructural
    FichaPuntoDeVenta ..|> Exportable : conformidad estructural