from typing import List
import json
from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from database import Invoice
from models.invoceResponceModel import InvoiceResponse  # Adjust import path as necessary
# import schemas 
from models.invoiceModel import  MercuryEXRF 
from models.invoiceModelDetailed import  DetailedReportDetails 
from pprint import pprint

from fastapi.encoders import jsonable_encoder 
router = APIRouter()
import logging



    
@router.get("" , response_model=List[InvoiceResponse])
async def get_invoices():
    invoices = await Invoice.find_all().to_list()
    return [invoice.dict(exclude={"_id"}) for invoice in invoices]

# create get invoice by id route
@router.get("/{invoice_id}" , response_model=InvoiceResponse)
async def get_invoice(invoice_id: str):
    invoiceData = await Invoice.find_one(Invoice.invoice_id == invoice_id)
    if invoiceData:
        return invoiceData
    raise HTTPException(status_code=404, detail="Invoice not found")



@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str):
    invoiceData = await Invoice.find_one(Invoice.invoice_id == invoice_id)
    if invoiceData:
        await invoiceData.delete()
        return {"message": "Invoice deleted successfully"}
    raise HTTPException(status_code=404, detail="Invoice not found")

def validate_mercury_exrf(data):
    # try:
    mercury_exrf_instance = MercuryEXRF(**data)
    return mercury_exrf_instance

