from dataclasses import dataclass
from typing import Literal
from datetime import datetime
from bson import ObjectId


@dataclass
class Transaction:
    """Modelo de transacción para la base de datos MongoDB.

    Este modelo representa la estructura de una transacción en la base de datos y contiene
    información relevante como el ID del usuario, el método de pago, la cantidad,
    la moneda, el estado de la transacción, el ID de la transacción del proveedor y
    la fecha de creación.
    """

    _id: ObjectId
    """ID único de la transacción en la base de datos."""

    user_id: ObjectId
    """ID del usuario que realizó la transacción.
    
    Clave foránea que referencia al modelo de usuario.
    """

    payment_method: ObjectId
    """ID del método de pago utilizado para la transacción.

    Clave foránea que referencia al modelo de método de pago.
    """

    amount: float
    """Cantidad de dinero involucrada en la transacción."""

    currency: str
    """Código de la moneda utilizada en la transacción."""

    status: Literal["successful", "failed", "pending"]
    """Estado de la transacción.

    Dependerá sobretodo del provedor de pago que maneje la transacción.

    successful: La transacción fue exitosa y se ha procesado correctamente.
    
    failed: La transacción falló y no se procesó.

    pending: La transacción está pendiente de ser procesada o confirmada.
    """

    provider_transacction_id: str
    """Identificador de la transacción proporcionado por el proveedor de pago."""

    created_at: datetime
    """Fecha y hora en que se creó la transacción.
    
    Utilizado solamente para fines de auditoría y registro.
    """
