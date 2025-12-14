from datetime import datetime, timedelta
import logging
import uuid
from enum import Enum
from typing import List, Dict, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"


class NotificationTemplate(str, Enum):
    WELCOME = "WELCOME"
    OTP_VERIFICATION = "OTP_VERIFICATION"
    LOI_ACCEPTANCE = "LOI_ACCEPTANCE"
    DOCUMENT_REQUEST = "DOCUMENT_REQUEST"
    DOCUMENT_RECEIVED = "DOCUMENT_RECEIVED"
    DOCUMENT_VERIFICATION_FAILED = "DOCUMENT_VERIFICATION_FAILED"
    UNDERWRITING_IN_PROGRESS = "UNDERWRITING_IN_PROGRESS"
    APPROVAL_NOTIFICATION = "APPROVAL_NOTIFICATION"
    REJECTION_NOTIFICATION = "REJECTION_NOTIFICATION"
    SANCTION_LETTER_READY = "SANCTION_LETTER_READY"
    SANCTION_LETTER_SENT = "SANCTION_LETTER_SENT"
    DISBURSEMENT_CONFIRMED = "DISBURSEMENT_CONFIRMED"
    EMI_REMINDER = "EMI_REMINDER"
    EMI_RECEIVED = "EMI_RECEIVED"
    PAYMENT_FAILED = "PAYMENT_FAILED"


class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    template_name: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    attachment_path: Optional[str] = None


class SMSRequest(BaseModel):
    phone_number: str
    message: str
    template_name: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None


class WhatsAppRequest(BaseModel):
    phone_number: str
    message: str
    template_name: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    media_url: Optional[str] = None


class NotificationRequest(BaseModel):
    customer_id: str
    customer_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notification_type: NotificationType
    template: NotificationTemplate
    variables: Optional[Dict[str, Any]] = None


app = FastAPI(
    title="Notification Server Mock",
    version="1.0",
    description="Mock Notification Server for sending emails, SMS, and WhatsApp",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


notification_log: List[Dict[str, Any]] = []
max_log_size = 1000


EMAIL_TEMPLATES: Dict[str, Dict[str, str]] = {
    "WELCOME": {
        "subject": "Welcome to Tata Capital - Personal Loan Application",
        "body": """
Dear {customer_name},

Welcome to Tata Capital! We're excited to help you achieve your financial goals.

We've received your interest in our personal loan products. Our team is ready to assist you with:
✓ Competitive interest rates
✓ Quick approval process
✓ Flexible repayment options
✓ Minimal documentation

Next Step: Please complete your application by uploading required documents.

Best regards,
Tata Capital Team
1800-TATA-LOAN
""",
    },
    "OTP_VERIFICATION": {
        "subject": "Your OTP for Tata Capital Verification",
        "body": """
Dear {customer_name},

Your One-Time Password (OTP) for verification is: {otp}

This OTP is valid for 10 minutes. Please do not share this with anyone.

If you didn't request this, please ignore this email.

Regards,
Tata Capital Team
""",
    },
}


SMS_TEMPLATES: Dict[str, str] = {
    "WELCOME": (
        "Welcome to Tata Capital! Your personal loan journey starts here. "
        "Download our app or visit {portal_link} to begin. Questions? Call 1800-TATA-LOAN"
    ),
    "OTP_VERIFICATION": "Your Tata Capital OTP is {otp}. Valid for 10 minutes. Do not share with anyone.",
}


WHATSAPP_TEMPLATES: Dict[str, str] = {
    "WELCOME": """
Hi {customer_name}! 👋

Welcome to Tata Capital!

We're excited to help you with your personal loan.

📱 Quick Actions:
• Apply Now: {portal_link}
• Check Status: {tracking_link}
• Need Help: 1800-TATA-LOAN

Let's get started! 🚀
""",
}


def generate_notification_id() -> str:
    return f"NOTIF_{uuid.uuid4().hex[:12].upper()}"


def format_template(template_body: str, variables: Dict[str, Any]) -> str:
    try:
        return template_body.format(**variables)
    except KeyError as exc:  # noqa: BLE001
        logger.warning("Missing variable in template: %s", str(exc))
        return template_body


def save_to_log(notification: Dict[str, Any]) -> None:
    notification_log.append(notification)
    if len(notification_log) > max_log_size:
        notification_log.pop(0)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "Notification Server Mock",
        "version": "1.0",
        "status": "running",
        "port": 8004,
        "description": "Mock Notification Server for emails, SMS, and WhatsApp",
        "endpoints_available": {
            "health": "/api/notification/health",
            "send_email": "/api/notification/send-email (POST)",
            "send_sms": "/api/notification/send-sms (POST)",
            "send_whatsapp": "/api/notification/send-whatsapp (POST)",
            "send_notification": "/api/notification/send (POST)",
            "notification_log": "/api/notification/log (GET)",
            "notification_status": "/api/notification/status/{notification_id} (GET)",
            "templates": "/api/notification/templates (GET)",
        },
    }


@app.get("/api/notification/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "Notification Server",
        "port": 8004,
        "timestamp": datetime.now().isoformat(),
        "notifications_sent": len(notification_log),
        "uptime": "Running",
    }


@app.post("/api/notification/send-email")
async def send_email(request: EmailRequest) -> Dict[str, Any]:
    logger.info("Email send request to: %s", request.to_email)

    notification_id = generate_notification_id()

    if request.template_name and request.template_name in EMAIL_TEMPLATES:
        template = EMAIL_TEMPLATES[request.template_name]
        subject = format_template(template["subject"], request.template_variables or {})
        body = format_template(template["body"], request.template_variables or {})
    else:
        subject = request.subject
        body = request.body

    notification = {
        "notification_id": notification_id,
        "type": NotificationType.EMAIL.value,
        "status": NotificationStatus.SENT.value,
        "to_email": request.to_email,
        "subject": subject,
        "body": body[:100] + "..." if len(body) > 100 else body,
        "sent_at": datetime.now().isoformat(),
        "delivered_at": None,
        "template": request.template_name,
        "attachment": request.attachment_path,
    }

    save_to_log(notification)

    logger.info("Email sent successfully. Notification ID: %s", notification_id)

    return {
        "status": "success",
        "data": {
            "notification_id": notification_id,
            "type": NotificationType.EMAIL.value,
            "status": NotificationStatus.SENT.value,
            "to_email": request.to_email,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "message": f"Email sent successfully to {request.to_email}",
        },
    }


@app.post("/api/notification/send-sms")
async def send_sms(request: SMSRequest) -> Dict[str, Any]:
    logger.info("SMS send request to: %s", request.phone_number)

    notification_id = generate_notification_id()

    if request.template_name and request.template_name in SMS_TEMPLATES:
        message = format_template(
            SMS_TEMPLATES[request.template_name], request.template_variables or {}
        )
    else:
        message = request.message

    sms_parts = (len(message) - 1) // 160 + 1

    notification = {
        "notification_id": notification_id,
        "type": NotificationType.SMS.value,
        "status": NotificationStatus.DELIVERED.value,
        "phone_number": request.phone_number,
        "message": message[:50] + "..." if len(message) > 50 else message,
        "sent_at": datetime.now().isoformat(),
        "delivered_at": datetime.now().isoformat(),
        "template": request.template_name,
        "sms_parts": sms_parts,
        "cost": f"Rs. {sms_parts * 1.5}",
    }

    save_to_log(notification)

    logger.info("SMS sent successfully. Notification ID: %s", notification_id)

    return {
        "status": "success",
        "data": {
            "notification_id": notification_id,
            "type": NotificationType.SMS.value,
            "status": NotificationStatus.DELIVERED.value,
            "phone_number": request.phone_number,
            "message": message,
            "sms_parts": sms_parts,
            "sent_at": datetime.now().isoformat(),
            "delivered_at": datetime.now().isoformat(),
            "message_detail": f"SMS sent successfully to {request.phone_number}",
        },
    }


@app.post("/api/notification/send-whatsapp")
async def send_whatsapp(request: WhatsAppRequest) -> Dict[str, Any]:
    logger.info("WhatsApp send request to: %s", request.phone_number)

    notification_id = generate_notification_id()

    if request.template_name and request.template_name in WHATSAPP_TEMPLATES:
        message = format_template(
            WHATSAPP_TEMPLATES[request.template_name], request.template_variables or {}
        )
    else:
        message = request.message

    notification = {
        "notification_id": notification_id,
        "type": NotificationType.WHATSAPP.value,
        "status": NotificationStatus.DELIVERED.value,
        "phone_number": request.phone_number,
        "message": message[:50] + "..." if len(message) > 50 else message,
        "sent_at": datetime.now().isoformat(),
        "delivered_at": datetime.now().isoformat(),
        "template": request.template_name,
        "media_url": request.media_url,
        "read_at": None,
    }

    save_to_log(notification)

    logger.info("WhatsApp sent successfully. Notification ID: %s", notification_id)

    return {
        "status": "success",
        "data": {
            "notification_id": notification_id,
            "type": NotificationType.WHATSAPP.value,
            "status": NotificationStatus.DELIVERED.value,
            "phone_number": request.phone_number,
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "delivered_at": datetime.now().isoformat(),
            "media_attached": request.media_url is not None,
            "message_detail": f"WhatsApp sent successfully to {request.phone_number}",
        },
    }


@app.post("/api/notification/send")
async def send_notification(request: NotificationRequest) -> Dict[str, Any]:
    logger.info("Multi-channel notification for customer: %s", request.customer_id)

    results: Dict[str, Any] = {
        "customer_id": request.customer_id,
        "customer_name": request.customer_name,
        "notifications_sent": [],
        "timestamp": datetime.now().isoformat(),
    }

    try:
        if request.notification_type == NotificationType.EMAIL and request.email:
            template = EMAIL_TEMPLATES.get(request.template.value, {})
            email_req = EmailRequest(
                to_email=request.email,
                subject=template.get("subject", "Tata Capital Notification"),
                body=template.get("body", ""),
                template_name=request.template.value,
                template_variables=request.variables or {},
            )
            response = await send_email(email_req)
            results["notifications_sent"].append(response["data"])
        elif request.notification_type == NotificationType.SMS and request.phone:
            sms_req = SMSRequest(
                phone_number=request.phone,
                message="",
                template_name=request.template.value,
                template_variables=request.variables or {},
            )
            response = await send_sms(sms_req)
            results["notifications_sent"].append(response["data"])
        elif request.notification_type == NotificationType.WHATSAPP and request.phone:
            whatsapp_req = WhatsAppRequest(
                phone_number=request.phone,
                message="",
                template_name=request.template.value,
                template_variables=request.variables or {},
            )
            response = await send_whatsapp(whatsapp_req)
            results["notifications_sent"].append(response["data"])

        results["status"] = "success"
        results["message"] = f"Notification sent via {request.notification_type.value}"
        return results
    except Exception as exc:  # noqa: BLE001
        logger.error("Error sending notification: %s", str(exc))
        return {
            "status": "error",
            "message": f"Failed to send notification: {str(exc)}",
        }


@app.post("/api/notification/send-bulk")
async def send_bulk_notification(request: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(
        "Bulk notification request for %s customers",
        len(request.get("notifications", [])),
    )

    notifications = request.get("notifications", [])
    template = request.get("template")

    results: Dict[str, Any] = {
        "status": "success",
        "template": template,
        "total_notifications": len(notifications),
        "sent_count": 0,
        "failed_count": 0,
        "notifications_sent": [],
        "timestamp": datetime.now().isoformat(),
    }

    for notif in notifications:
        try:
            if notif.get("email"):
                email_req = EmailRequest(
                    to_email=notif["email"],
                    subject="Tata Capital Notification",
                    body="",
                    template_name=template,
                    template_variables=notif.get("variables", {}),
                )
                email_response = await send_email(email_req)
                results["sent_count"] += 1
                results["notifications_sent"].append(
                    {
                        "customer_id": notif.get("customer_id"),
                        "email": email_response["data"]["notification_id"],
                        "status": "sent",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Error sending to %s: %s", notif.get("customer_id"), str(exc)
            )
            results["failed_count"] += 1

    return results


@app.get("/api/notification/status/{notification_id}")
async def get_notification_status(notification_id: str):
    logger.info("Status check for notification: %s", notification_id)

    for notif in notification_log:
        if notif["notification_id"] == notification_id:
            return {"status": "success", "data": notif}

    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": f"Notification {notification_id} not found",
        },
    )


@app.get("/api/notification/log")
async def get_notification_log(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    logger.info("Notification log request - limit: %s, offset: %s", limit, offset)

    sorted_log = sorted(
        notification_log,
        key=lambda x: x["sent_at"],
        reverse=True,
    )

    slice_ = sorted_log[offset : offset + limit]

    return {
        "status": "success",
        "data": {
            "total_count": len(notification_log),
            "limit": limit,
            "offset": offset,
            "returned_count": len(slice_),
            "notifications": slice_,
        },
    }


@app.get("/api/notification/templates")
async def get_all_templates() -> Dict[str, Any]:
    logger.info("All templates request")

    return {
        "status": "success",
        "data": {
            "email_templates": list(EMAIL_TEMPLATES.keys()),
            "sms_templates": list(SMS_TEMPLATES.keys()),
            "whatsapp_templates": list(WHATSAPP_TEMPLATES.keys()),
            "total_templates": (
                len(EMAIL_TEMPLATES)
                + len(SMS_TEMPLATES)
                + len(WHATSAPP_TEMPLATES)
            ),
        },
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request, exc: HTTPException
) -> JSONResponse:  # type: ignore[override]
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request, exc: Exception
) -> JSONResponse:  # type: ignore[override]
    logger.error("Unexpected error: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("%s", "=" * 80)
    logger.info("NOTIFICATION SERVER MOCK STARTED")
    logger.info("%s", "=" * 80)
    logger.info("Port: 8004")
    logger.info("Email templates: %d", len(EMAIL_TEMPLATES))
    logger.info("SMS templates: %d", len(SMS_TEMPLATES))
    logger.info("WhatsApp templates: %d", len(WHATSAPP_TEMPLATES))
    logger.info("Timestamp: %s", datetime.now().isoformat())
    logger.info("%s", "=" * 80)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("%s", "=" * 80)
    logger.info("NOTIFICATION SERVER MOCK SHUTTING DOWN")
    logger.info("Total notifications sent: %d", len(notification_log))
    logger.info("Timestamp: %s", datetime.now().isoformat())
    logger.info("%s", "=" * 80)


if __name__ == "__main__":
    print("=" * 80)
    print("NOTIFICATION SERVER MOCK")
    print("=" * 80)
    print("Starting Notification Server on http://0.0.0.0:8004")
    print("API Documentation: http://localhost:8004/docs")
    print("ReDoc Documentation: http://localhost:8004/redoc")
    print(f"Email Templates: {len(EMAIL_TEMPLATES)}")
    print(f"SMS Templates: {len(SMS_TEMPLATES)}")
    print(f"WhatsApp Templates: {len(WHATSAPP_TEMPLATES)}")
    print("=" * 80)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info",
        reload=False,
    )
