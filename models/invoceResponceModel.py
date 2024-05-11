from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from models.invoiceModel import Approver, Details, Reporter

# Assuming this is your detailed transaction data model adjusted for response
class DetailedTransactionDataResponse(BaseModel):
    date: datetime
    type: str
    amount: float
    currency: str

# Adjusted Transaction response model
class DetailedTransactionResponse(BaseModel):
    data: DetailedTransactionDataResponse
    reference: str
    details: str

# Response model for the invoice excluding _id
class InvoiceResponse(BaseModel):
    id: str = Field(..., alias='invoice_id')  # Assuming you want to keep this as 'id' in the response
    reporter: Reporter  # Assuming Reporter is defined elsewhere as shown in your example
    approvers: List[Approver]  # Assuming Approver is defined elsewhere
    transactions: List[DetailedTransactionResponse]
    details: Details  # Assuming Details is defined elsewhere

