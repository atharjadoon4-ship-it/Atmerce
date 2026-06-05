import os
import asyncio
import logging
import resend
from typing import Optional

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")

if RESEND_API_KEY and RESEND_API_KEY != "re_placeholder_add_your_key_here":
    resend.api_key = RESEND_API_KEY
    logger.info("Resend email service initialized")
else:
    logger.warning("RESEND_API_KEY not configured - email notifications disabled")

async def send_email(to_email: str, subject: str, html_content: str) -> Optional[dict]:
    """Send email using Resend."""
    if not RESEND_API_KEY or RESEND_API_KEY == "re_placeholder_add_your_key_here":
        logger.warning(f"Email not sent (no API key): {subject} to {to_email}")
        return {"status": "skipped", "reason": "API key not configured"}
    
    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {subject}")
        return {"status": "sent", "email_id": result.get("id")}
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return {"status": "failed", "error": str(e)}

def get_order_confirmation_email(order_id: str, customer_name: str, total: float, items: list) -> str:
    """Generate order confirmation email HTML."""
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${item['price'] * item['quantity']:.2f}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #FF9900; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h1 style="color: white; margin: 0;">Order Confirmed!</h1>
        </div>
        <div style="background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-radius: 0 0 5px 5px;">
            <p>Hi {customer_name},</p>
            <p>Thank you for your order! We're processing it and will send you another email when it ships.</p>
            
            <h2 style="color: #FF9900; border-bottom: 2px solid #FF9900; padding-bottom: 10px;">Order Details</h2>
            <p><strong>Order ID:</strong> {order_id}</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #f0f0f0;">
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Item</th>
                        <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Qty</th>
                        <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Price</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="2" style="padding: 15px 10px; text-align: right; font-weight: bold;">Total:</td>
                        <td style="padding: 15px 10px; text-align: right; font-weight: bold; font-size: 1.2em; color: #FF9900;">${total:.2f}</td>
                    </tr>
                </tfoot>
            </table>
            
            <p>You can track your order status in your account dashboard.</p>
            <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666;">
                Questions? Reply to this email or contact our support team.
            </p>
        </div>
    </body>
    </html>
    """

def get_order_status_email(order_id: str, customer_name: str, status: str) -> str:
    """Generate order status update email HTML."""
    status_messages = {
        "processing": "Your order is being prepared",
        "shipped": "Your order has been shipped!",
        "delivered": "Your order has been delivered"
    }
    
    status_colors = {
        "processing": "#F59E0B",
        "shipped": "#3B82F6",
        "delivered": "#10B981"
    }
    
    message = status_messages.get(status, "Order status updated")
    color = status_colors.get(status, "#FF9900")
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: {color}; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h1 style="color: white; margin: 0;">{message}</h1>
        </div>
        <div style="background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-radius: 0 0 5px 5px;">
            <p>Hi {customer_name},</p>
            <p>Your order status has been updated.</p>
            
            <div style="background-color: white; padding: 15px; border-left: 4px solid {color}; margin: 20px 0;">
                <p style="margin: 0;"><strong>Order ID:</strong> {order_id}</p>
                <p style="margin: 10px 0 0 0;"><strong>Status:</strong> <span style="color: {color}; text-transform: uppercase;">{status}</span></p>
            </div>
            
            <p>You can track your order in your account dashboard for real-time updates.</p>
            <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666;">
                Questions? Reply to this email or contact our support team.
            </p>
        </div>
    </body>
    </html>
    """