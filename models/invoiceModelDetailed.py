from datetime import datetime
from pydantic import BaseModel, EmailStr, Field,ConfigDict,computed_field
from typing import List, Optional
from enum import Enum, IntEnum
from datetime import datetime, timezone
from typing import Any, Dict
from typing_extensions import Annotated
from pydantic import BaseModel, WrapSerializer

from models.invoiceModel import Transaction, ReportDetails
    
class DetailedTransactionData(BaseModel):
    date: datetime
    type: str
    amount: float
    currency: str

class DetailedTransaction(Transaction):
    data :  DetailedTransactionData 

class DetailedReportDetails(ReportDetails):
    transactions: List[DetailedTransaction]
