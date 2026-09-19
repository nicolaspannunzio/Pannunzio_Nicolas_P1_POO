"""main.py

Demostración ejecutable del catálogo de Food Store.
Valida el funcionamiento de los Requerimientos 1 al 5
"""

from catalogo import (
    Categoria,
    ErrorDominio,
    Producto,
    ProductoCombo,
    ProductoDestacado,
    ProductoPorPeso,
    ProductoSimple,
    UnidadMedida,
    exportar_catalogo,
)
from libreria_externa import FichaPuntoDeVenta


# Subclase incompleta para demostrar Falla Temprana en tiempo de construcción
class SubclaseIncompleta(Producto):
    """Subclase de prueba que no implementa precio_final()."""


def ejecutar_demo() -> None:
    print("=" * 70)
    print("DEMOSTRACIÓN EVALUATIVA - PROGRAMACIÓN IV (UTN)")
    print("Food Store: Catálogo Modular y Decisiones de Diseño")
    print("=" * 70)

    # -----------------------------------------------------------------
    # 1. Unidades de Medida y Categorías
    # -----------------------------------------------------------------
    print("\n--- 1. DEFINICIÓN DE UNIDADES Y CATEGORÍAS ---")
    u_kg = UnidadMedida(nombre="Kilogramo", simbolo="kg", tipo="masa")
    u_u = UnidadMedida(nombre="Unidad", simbolo="u", tipo="unidad")
    u_litro = UnidadMedida(nombre="Litro", simbolo="L", tipo="volumen")

    cat_almacen = Categoria("Almacén", "Productos secos y enlatados")
    cat_bebidas = Categoria("Bebidas", "Aguas, jugos y refrescos")
    cat_fiambreria = Categoria("Fiambrería", "Quesos y fiambres al peso")
    cat_promociones = Categoria("Promociones", "Combos y ofertas especiales")

    print(f"Unidad de Medida creada: {u_kg.nombre} ({u_kg.simbolo})")
    print(f"Categoría creada: {cat_almacen.nombre} - {cat_almacen.descripcion}")

    # -----------------------------------------------------------------
    # 2. Creación de Productos Base (Componentes de combo y catálogo)
    # -----------------------------------------------------------------
    print("\n--- 2. CREACIÓN DE PRODUCTOS INDIVIDUALES ---")
    pan = ProductoSimple("Pan Baguette", 1500.0, 30.0, cat_almacen, u_u)
    gaseosa = ProductoSimple("Gaseosa Cola 1.5L", 2500.0, 20.0, cat_bebidas, u_litro)
    jamon = ProductoPorPeso("Jamón Cocido", 12000.0, 15.0, cat_fiambreria, u_kg)
    queso = ProductoPorPeso("Queso Dambo", 9500.0, 25.0, cat_fiambreria, u_kg)

    print(f"Producto Simple: {pan.nombre} | Publicado: {pan.precio_publicado}")
    print(f"Producto por Peso: {jamon.nombre} | Publicado: {jamon.precio_publicado}")

    # -----------------------------------------------------------------
    # 3. Agregación: Creación de Combos (Req. 2 y 3)
    # -----------------------------------------------------------------
    print("\n--- 3. AGREGACIÓN EN PRODUCTO COMBO ---")
    # Combo 1: Pan + Gaseosa (10% descuento)
    combo_picnic = ProductoCombo(
        nombre="Combo Picnic",
        categoria_principal=cat_promociones,
        componentes=[pan, gaseosa],
        descuento=0.10,
        stock_cantidad=8.0,
    )
    # Combo 2: Jamón + Queso (15% descuento)
    combo_fiambreria = ProductoCombo(
        nombre="Combo Fiambrería Exprés",
        categoria_principal=cat_promociones,
        componentes=[jamon, queso],
        descuento=0.15,
        stock_cantidad=5.0,
    )

    print(f"Combo creado: {combo_picnic.nombre} | Precio publicado: {combo_picnic.precio_publicado}")
    print(f"  Componentes agregados: {[c.nombre for c in combo_picnic.componentes()]}")
    print("  Evidencia de Agregación: los componentes existían antes y siguen existiendo independientes.")

    # -----------------------------------------------------------------
    # 4. Catálogo con al menos 4 productos (sin contar componentes)
    # -----------------------------------------------------------------
    print("\n--- 4. CATÁLOGO PRINCIPAL Y POLIMORFISMO DE PRECIOS ---")
    cerveza = ProductoSimple("Cerveza Artesanal", 3200.0, 12.0, cat_bebidas, u_litro)
    bondiola = ProductoPorPeso("Bondiola Serrana", 14500.0, 10.0, cat_fiambreria, u_kg)

    # 4 productos principales distintos de los componentes aislados
    catalogo_principal: list[Producto] = [cerveza, bondiola, combo_picnic, combo_fiambreria]

    # Cobro polimórfico sin if/elif ni isinstance()
    cantidades_pedido = [2.0, 0.350, 1.0, 2.0]
    for prod, cant in zip(catalogo_principal, cantidades_pedido, strict=True):
        total = prod.precio_final(cant)
        print(f"* {prod.nombre} | Cant: {cant} -> Precio Final: $ {total:.2f}")

    # -----------------------------------------------------------------
    # 5. Demostración de Composición e Invariante de Categoría (Req. 2)
    # -----------------------------------------------------------------
    print("\n--- 5. COMPOSICIÓN E INVARIANTE DE CATEGORÍAS ---")
    print(f"Categoría principal original de Cerveza: {cerveza.categoria_principal().nombre}")
    cerveza.clasificar_en(cat_promociones, es_principal=True)
    print(f"Nueva categoría principal (cambio dinámico): {cerveza.categoria_principal().nombre}")
    print(f"Total de vínculos del producto: {len(cerveza.categorias())}")

    # Intento de mutar la tupla retornada
    try:
        cerveza.categorias().append(None)  # type: ignore
    except AttributeError:
        print("Protección de colección: categorias() devuelve una tupla inmutable (AttributeError).")

    # -----------------------------------------------------------------
    # 6. Demostración de ProductoDestacado (Rediseño Req. 3 - HU-P1-05)
    # -----------------------------------------------------------------
    print("\n--- 6. PRODUCTOS DESTACADOS EN VIDRIERA (REDISEÑO) ---")
    destacado_peso = ProductoDestacado(producto=bondiola, orden_vidriera=1)
    destacado_combo = ProductoDestacado(producto=combo_picnic, orden_vidriera=2)
    print(f"Destacado 1: {destacado_peso.exportar()}")
    print(f"Destacado 2: {destacado_combo.exportar()}")
    print("Evidencia: el rediseño por asociación permite destacar cualquier subtipo sin tocar la herencia.")

    # -----------------------------------------------------------------
    # 7. Contrato Exportable y Protocol con Librería Externa (Req. 4)
    # -----------------------------------------------------------------
    print("\n--- 7. EXPORTACIÓN HETEROGÉNEA (PROTOCOL EXPORTABLE) ---")
    ficha_pos = FichaPuntoDeVenta(codigo="POS-884", detalle="Ticket Fiscal Apertura")

    items_a_exportar = [cerveza, bondiola, combo_picnic, ficha_pos]
    resultado_exportacion = exportar_catalogo(items_a_exportar)

    for linea in resultado_exportacion:
        print(f"  [EXPORT] {linea}")

    # -----------------------------------------------------------------
    # 8. Demostración de Fallas Tempranas y Validaciones de Dominio
    # -----------------------------------------------------------------
    print("\n--- 8. VALIDACIONES DE DOMINIO Y FALLA TEMPRANA ---")
    try:
        Producto("Producto Inválido", 100.0, 10.0, cat_almacen)  # type: ignore
    except TypeError:
        print("Falla Temprana 1: No se puede instanciar directamente Producto abstracto (TypeError).")

    try:
        SubclaseIncompleta("Incompleto", 100.0, 10.0, cat_almacen)
    except TypeError:
        print("Falla Temprana 2: Subclase sin precio_final() falla al construir (TypeError).")

    try:
        pan.precio_final(2.5)
    except ErrorDominio as err:
        print(f"Validación Simple: {err}")

    try:
        ProductoCombo("Combo Fallido", cat_promociones, [pan], 0.10)
    except ErrorDominio as err:
        print(f"Validación Combo: {err}")

    print("\n" + "=" * 70)
    print("DEMOSTRACIÓN FINALIZADA CON ÉXITO")
    print("=" * 70)


if __name__ == "__main__":
    ejecutar_demo()