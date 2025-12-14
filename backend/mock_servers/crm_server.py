from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Tata Capital CRM Mock Server", version="1.0")


# In-memory database (mock)
customers_db = {
    "ABCDE1234F": {  # PAN Number
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "9876543210",
        "pan_number": "ABCDE1234F",
        "monthly_income": 75000,
        "employment_type": "EMPLOYED",
        "company_name": "ABC Corporation",
        "years_employed": 3,
        "address": "123 Main St, Mumbai",
        "bank_account": "1234567890",
        "bank_ifsc": "HDFC0000001",
        "previous_loan_applications": 1,
        "previous_loan_amount": 200000,
        "previous_loan_status": "CLOSED",
        "created_at": "2024-06-15",
    },
    "PQRST5678G": {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane.smith@email.com",
        "phone": "9876543211",
        "pan_number": "PQRST5678G",
        "monthly_income": 85000,
        "employment_type": "EMPLOYED",
        "company_name": "XYZ Ltd",
        "years_employed": 5,
        "address": "456 Oak Ave, Bangalore",
        "bank_account": "0987654321",
        "bank_ifsc": "ICIC0000002",
        "previous_loan_applications": 0,
        "previous_loan_amount": 0,
        "previous_loan_status": None,
        "created_at": "2024-08-20",
    },
}


additional_customers = [
    {
        "id": 3,
        "name": "Rajesh Kumar",
        "email": "rajesh.k@email.com",
        "phone": "9876543212",
        "pan_number": "MNOPQ9101H",
        "monthly_income": 65000,
        "employment_type": "EMPLOYED",
        "company_name": "Tech Solutions",
        "years_employed": 2,
        "address": "789 Pine Rd, Delhi",
        "bank_account": "1111111111",
        "bank_ifsc": "AXIS0000003",
        "previous_loan_applications": 2,
        "previous_loan_amount": 150000,
        "previous_loan_status": "ACTIVE",
        "created_at": "2025-01-10",
    },
    {
        "id": 4,
        "name": "Priya Sharma",
        "email": "priya.s@email.com",
        "phone": "9876543213",
        "pan_number": "XYZU11121I",
        "monthly_income": 95000,
        "employment_type": "SELF_EMPLOYED",
        "company_name": "Sharma Consultants",
        "years_employed": 4,
        "address": "321 Elm St, Pune",
        "bank_account": "2222222222",
        "bank_ifsc": "BOBI0000004",
        "previous_loan_applications": 1,
        "previous_loan_amount": 300000,
        "previous_loan_status": "CLOSED",
        "created_at": "2025-02-15",
    },
    {
        "id": 5,
        "name": "Amit Patel",
        "email": "amit.p@email.com",
        "phone": "9876543214",
        "pan_number": "CDEF21234J",
        "monthly_income": 55000,
        "employment_type": "EMPLOYED",
        "company_name": "Finance Corp",
        "years_employed": 1,
        "address": "654 Maple Dr, Hyderabad",
        "bank_account": "3333333333",
        "bank_ifsc": "SBIN0000005",
        "previous_loan_applications": 0,
        "previous_loan_amount": 0,
        "previous_loan_status": None,
        "created_at": "2025-03-10",
    },
    {
        "id": 6,
        "name": "Neha Gupta",
        "email": "neha.g@email.com",
        "phone": "9876543215",
        "pan_number": "GHIJ31245K",
        "monthly_income": 120000,
        "employment_type": "EMPLOYED",
        "company_name": "Tech Giant",
        "years_employed": 6,
        "address": "987 Cedar Ln, Gurgaon",
        "bank_account": "4444444444",
        "bank_ifsc": "HDFC0000006",
        "previous_loan_applications": 3,
        "previous_loan_amount": 500000,
        "previous_loan_status": "CLOSED",
        "created_at": "2025-04-05",
    },
    {
        "id": 7,
        "name": "Vikram Singh",
        "email": "vikram.s@email.com",
        "phone": "9876543216",
        "pan_number": "KLMN41256L",
        "monthly_income": 45000,
        "employment_type": "EMPLOYED",
        "company_name": "Retail Store",
        "years_employed": 2,
        "address": "147 Birch St, Ahmedabad",
        "bank_account": "5555555555",
        "bank_ifsc": "ICIC0000007",
        "previous_loan_applications": 1,
        "previous_loan_amount": 100000,
        "previous_loan_status": "ACTIVE",
        "created_at": "2025-05-12",
    },
    {
        "id": 8,
        "name": "Deepika Malhotra",
        "email": "deepika.m@email.com",
        "phone": "9876543217",
        "pan_number": "OPQR51267M",
        "monthly_income": 110000,
        "employment_type": "SELF_EMPLOYED",
        "company_name": "Design Studio",
        "years_employed": 5,
        "address": "258 Walnut Ave, Jaipur",
        "bank_account": "6666666666",
        "bank_ifsc": "AXIS0000008",
        "previous_loan_applications": 2,
        "previous_loan_amount": 250000,
        "previous_loan_status": "CLOSED",
        "created_at": "2025-06-08",
    },
    {
        "id": 9,
        "name": "Sanjay Verma",
        "email": "sanjay.v@email.com",
        "phone": "9876543218",
        "pan_number": "STUV61278N",
        "monthly_income": 70000,
        "employment_type": "EMPLOYED",
        "company_name": "Energy Solutions",
        "years_employed": 3,
        "address": "369 Spruce Rd, Lucknow",
        "bank_account": "7777777777",
        "bank_ifsc": "BOBI0000009",
        "previous_loan_applications": 0,
        "previous_loan_amount": 0,
        "previous_loan_status": None,
        "created_at": "2025-07-14",
    },
    {
        "id": 10,
        "name": "Anjali Reddy",
        "email": "anjali.r@email.com",
        "phone": "9876543219",
        "pan_number": "WXYZ71289O",
        "monthly_income": 88000,
        "employment_type": "EMPLOYED",
        "company_name": "Manufacturing Co",
        "years_employed": 4,
        "address": "741 Fir Lane, Chennai",
        "bank_account": "8888888888",
        "bank_ifsc": "SBIN0000010",
        "previous_loan_applications": 1,
        "previous_loan_amount": 180000,
        "previous_loan_status": "ACTIVE",
        "created_at": "2025-08-20",
    },
]


for customer in additional_customers:
    customers_db[customer["pan_number"]] = customer


class CustomerRequest(BaseModel):
    pan_number: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    pan_number: str
    monthly_income: float
    employment_type: str
    company_name: str
    years_employed: int
    address: str
    bank_account: str
    bank_ifsc: str


@app.post("/api/crm/get-customer")
async def get_customer(request: CustomerRequest):
    """Fetch customer details by PAN number."""

    if request.pan_number in customers_db:
        return {
            "status": "success",
            "data": customers_db[request.pan_number],
        }

    return {
        "status": "error",
        "message": f"Customer with PAN {request.pan_number} not found",
        "data": None,
    }


@app.get("/api/crm/all-customers")
async def get_all_customers():
    """Get all dummy customers (for testing/demo purposes)."""

    return {
        "status": "success",
        "count": len(customers_db),
        "data": list(customers_db.values()),
    }


@app.post("/api/crm/create-customer")
async def create_customer(customer: CustomerResponse):
    """Create a new customer record."""

    if customer.pan_number in customers_db:
        return {
            "status": "error",
            "message": "Customer with this PAN already exists",
        }

    customers_db[customer.pan_number] = customer.dict()

    return {
        "status": "success",
        "message": "Customer created successfully",
        "data": customer,
    }


@app.put("/api/crm/update-customer/{pan_number}")
async def update_customer(pan_number: str, customer_data: dict):
    """Update customer information."""

    if pan_number not in customers_db:
        return {
            "status": "error",
            "message": "Customer not found",
        }

    customers_db[pan_number].update(customer_data)

    return {
        "status": "success",
        "message": "Customer updated successfully",
        "data": customers_db[pan_number],
    }


@app.get("/api/crm/customer-history/{pan_number}")
async def get_customer_history(pan_number: str):
    """Get customer's loan application history."""

    if pan_number not in customers_db:
        return {
            "status": "error",
            "message": "Customer not found",
        }

    customer = customers_db[pan_number]

    return {
        "status": "success",
        "data": {
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "previous_applications": customer["previous_loan_applications"],
            "previous_loan_amount": customer["previous_loan_amount"],
            "previous_loan_status": customer["previous_loan_status"],
            "loan_history": [
                {
                    "application_id": 1001,
                    "amount": customer["previous_loan_amount"],
                    "status": customer["previous_loan_status"],
                    "date": "2023-06-15",
                }
            ]
            if customer["previous_loan_amount"] > 0
            else [],
        },
    }


@app.get("/api/crm/health")
async def health_check():
    """Health check endpoint."""

    return {
        "status": "healthy",
        "service": "CRM Server",
        "port": 8001,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
