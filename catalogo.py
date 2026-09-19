"""catalogo.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


# =====================================================================
# Excepciones de Dominio (Req. 1)
# =====================================================================
class ErrorDominio(ValueError):
    """Excepción base para violaciones de reglas de negocio del catálogo."""


# =====================================================================
# Objetos de Valor y Entidades Base (Req. 1)
# =====================================================================
@dataclass(frozen=True)
class UnidadMedida:
    """Objeto de valor inmutable que representa la unidad de venta."""

    nombre: str
    simbolo: str
    tipo: str


class Categoria:
    """Clasificación del catálogo. Expone atributos en solo lectura."""

    def __init__(self, nombre: str, descripcion: str = "") -> None:
        if not nombre or not nombre.strip():
            raise ErrorDominio("El nombre de la categoría no puede estar vacío.")
        self._nombre: str = nombre.strip()
        self._descripcion: str = descripcion.strip()

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def descripcion(self) -> str:
        return self._descripcion


# =====================================================================
# Vínculo de Composición (Req. 2)
# =====================================================================
class ProductoCategoria:
    """Vínculo entre Producto y Categoría con estado de principalidad.

    Su ciclo de vida está gobernado exclusivamente por su Producto dueño.
    """

    def __init__(self, categoria: Categoria, es_principal: bool) -> None:
        self._categoria: Categoria = categoria
        self._es_principal: bool = es_principal

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    @property
    def es_principal(self) -> bool:
        return self._es_principal

    def _marcar_principal(self, valor: bool) -> None:
        """Método protegido de dominio accesible solo por su Producto contenedor."""
        self._es_principal = valor


# =====================================================================
# Clase Abstracta Producto (Req. 1, 2 y 3)
# =====================================================================
class Producto(ABC):
    """Clase base abstracta del catálogo."""

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        stock_cantidad: float,
        categoria_principal: Categoria,
        unidad_venta: UnidadMedida | None = None,
    ) -> None:
        if not nombre or not nombre.strip():
            raise ErrorDominio("El nombre del producto no puede estar vacío.")
        if precio_base < 0:
            raise ErrorDominio("El precio base no puede ser negativo.")
        if stock_cantidad < 0:
            raise ErrorDominio("El stock no puede ser negativo.")
        if not isinstance(categoria_principal, Categoria):
            raise ErrorDominio("La categoría principal debe ser una instancia de Categoria.")

        self._nombre: str = nombre.strip()
        self._precio_base: float = float(precio_base)
        self._stock_cantidad: float = float(stock_cantidad)
        self._habilitado: bool = True
        self._unidad_venta: UnidadMedida | None = unidad_venta

        # Composición: Producto fabrica y gestiona sus vínculos
        self._clasificaciones: list[ProductoCategoria] = []
        primer_vinculo = ProductoCategoria(categoria_principal, es_principal=True)
        self._clasificaciones.append(primer_vinculo)

    # --- Properties de Lectura (Req. 1) ---
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @property
    def stock_cantidad(self) -> float:
        return self._stock_cantidad

    @property
    def unidad_venta(self) -> UnidadMedida | None:
        return self._unidad_venta

    @property
    def disponible(self) -> bool:
        """True solo si el producto está habilitado y tiene stock positivo."""
        return self._habilitado and self._stock_cantidad > 0

    @property
    def precio_publicado(self) -> str:
        """Formatea el precio según tenga o no unidad de medida."""
        if self._unidad_venta is not None:
            return f"$ {self._precio_base:.2f} / {self._unidad_venta.simbolo}"
        return f"$ {self._precio_base:.2f}"

    # --- Gestión de Estado ---
    def habilitar(self) -> None:
        self._habilitado = True

    def deshabilitar(self) -> None:
        self._habilitado = False

    # --- Gestión de Clasificaciones (Req. 2) ---
    def clasificar_en(self, categoria: Categoria, es_principal: bool = False) -> None:
        """Agrega una clasificación respetando la unicidad y el invariante principal."""
        if not isinstance(categoria, Categoria):
            raise ErrorDominio("Se requiere una instancia válida de Categoria.")

        for vinculo in self._clasificaciones:
            if vinculo.categoria is categoria:
                raise ErrorDominio(
                    f"El producto ya está clasificado en la categoría '{categoria.nombre}'."
                )

        if es_principal:
            for vinculo in self._clasificaciones:
                vinculo._marcar_principal(False)

        nuevo_vinculo = ProductoCategoria(categoria, es_principal=es_principal)
        self._clasificaciones.append(nuevo_vinculo)

    def categorias(self) -> tuple[ProductoCategoria, ...]:
        """Retorno protegido: tupla inmutable copia de la lista interna."""
        return tuple(self._clasificaciones)

    def categoria_principal(self) -> Categoria:
        """Devuelve la Categoria principal garantizando el invariante."""
        for vinculo in self._clasificaciones:
            if vinculo.es_principal:
                return vinculo.categoria
        raise ErrorDominio("Invariante roto: el producto no posee categoría principal.")

    # --- Contrato Exportable (Req. 4) ---
    def exportar(self) -> str:
        """Representación exportable del producto."""
        return f"PRODUCTO {self._nombre} | {self.precio_publicado} | Stock: {self._stock_cantidad}"

    # --- Método Abstracto (Req. 3) ---
    @abstractmethod
    def precio_final(self, cantidad: float) -> float:
        """Calcula el precio final según las reglas del tipo de venta."""


# =====================================================================
# Subclases Polimórficas de Producto (Req. 3)
# =====================================================================
class ProductoSimple(Producto):
    """Producto vendido por pieza unitaria."""

    def precio_final(self, cantidad: float) -> float:
        if not isinstance(cantidad, (int, float)) or not float(cantidad).is_integer():
            raise ErrorDominio("La cantidad para un producto simple debe ser un valor entero.")
        if cantidad < 1:
            raise ErrorDominio("La cantidad debe ser mayor o igual a 1.")
        return self._precio_base * cantidad


class ProductoPorPeso(Producto):
    """Producto vendido por masa, admite cantidades decimales."""

    def precio_final(self, cantidad: float) -> float:
        if not isinstance(cantidad, (int, float)) or cantidad <= 0:
            raise ErrorDominio("La cantidad debe ser numérica y mayor a 0.")
        return round(self._precio_base * cantidad, 2)


class ProductoCombo(Producto):
    """Producto compuesto por agregación de 2 o más componentes."""

    def __init__(
        self,
        nombre: str,
        categoria_principal: Categoria,
        componentes: list[Producto],
        descuento: float,
        stock_cantidad: float = 10.0,
        unidad_venta: UnidadMedida | None = None,
    ) -> None:
        if len(componentes) < 2:
            raise ErrorDominio("Un combo debe estar compuesto por al menos 2 productos.")
        for comp in componentes:
            if not isinstance(comp, Producto):
                raise ErrorDominio("Todos los componentes deben ser instancias de Producto.")
        if not (0.0 <= descuento < 1.0):
            raise ErrorDominio("El descuento debe encontrarse en el rango [0, 1).")

        # Agregación: componentes ya existen independientemente
        self._componentes: list[Producto] = list(componentes)
        self._descuento: float = float(descuento)

        # Precio base derivado de la suma de componentes con descuento aplicado
        precio_base_calculado = sum(c.precio_final(1) for c in self._componentes) * (1 - self._descuento)

        super().__init__(
            nombre=nombre,
            precio_base=precio_base_calculado,
            stock_cantidad=stock_cantidad,
            categoria_principal=categoria_principal,
            unidad_venta=unidad_venta,
        )

    @property
    def descuento(self) -> float:
        return self._descuento

    def componentes(self) -> tuple[Producto, ...]:
        """Retorno protegido: tupla inmutable de componentes agregados."""
        return tuple(self._componentes)

    def precio_final(self, cantidad: float) -> float:
        if not isinstance(cantidad, (int, float)) or not float(cantidad).is_integer():
            raise ErrorDominio("La cantidad para un combo debe ser un valor entero.")
        if cantidad < 1:
            raise ErrorDominio("La cantidad debe ser mayor o igual a 1.")

        suma_componentes = sum(c.precio_final(1) for c in self._componentes)
        return suma_componentes * (1 - self._descuento) * cantidad


# =====================================================================
# Rediseño de ProductoDestacado (Req. 3 - HU-P1-05)
# =====================================================================
class ProductoDestacado:
    """Envoltorio / Vínculo de vidriera para destacar cualquier tipo de producto.

    Rediseñado mediante Composición/Asociación para evitar la herencia indebida.
    """

    def __init__(self, producto: Producto, orden_vidriera: int) -> None:
        if not isinstance(producto, Producto):
            raise ErrorDominio("El elemento a destacar debe ser un Producto.")
        if orden_vidriera < 1:
            raise ErrorDominio("El orden de vidriera debe ser un entero positivo.")
        self._producto: Producto = producto
        self._orden_vidriera: int = orden_vidriera

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def orden_vidriera(self) -> int:
        return self._orden_vidriera

    def exportar(self) -> str:
        return f"DESTACADO [Orden {self._orden_vidriera}] -> {self._producto.exportar()}"


# =====================================================================
# Contrato y Función de Exportación (Req. 4)
# =====================================================================
class Exportable(Protocol):
    """Contrato estructural (Protocol) para exportación."""

    def exportar(self) -> str:
        ...


def exportar_catalogo(items: list[Exportable]) -> list[str]:
    """Exporta en una sola operación cualquier elemento que implemente exportar()."""
    return [item.exportar() for item in items]