import os
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def create_payment_session(payment, student, success_url, cancel_url):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": payment.description},
                "unit_amount": int(payment.amount * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=student.email,
        metadata={
            "payment_id": str(payment.id),
            "student_id": str(student.id),
        },
    )
    return session