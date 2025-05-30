from app.services.customer_service import (
    create_customer, get_all_customers, get_customer_by_id,
    update_customer, delete_customer, add_loyalty_points, apply_discount
)
from sqlalchemy.exc import IntegrityError


def run_tests():
    print("=== Creating Customers ===")
    try:
        c1 = create_customer(
            "Alice Wanjiku", "alice@example.com", phone="0711222333")
        c2 = create_customer("Bob Oduor", "bob@example.com",
                             customer_type="business", company_name="Oduor Ltd", discount_rate=10)
        print(f"Created: {c1}")
        print(f"Created: {c2}")
    except IntegrityError as e:
        print(f"Integrity Error: {e}")

    print("\n=== All Customers ===")
    customers = get_all_customers()
    for customer in customers:
        print(customer)

    print("\n=== Get Single Customer ===")
    customer = get_customer_by_id(1)
    print(customer)

    print("\n=== Update Customer ===")
    updated = update_customer(1, name="Alice W. Njenga", phone="0799999999")
    print(f"Updated: {updated}")

    print("\n=== Loyalty Points ===")
    add_loyalty_points(1, 50)
    print(f"Added points: {get_customer_by_id(1)}")

    print("\n=== Apply Discount ===")
    apply_discount(2, 20)
    print(f"Applied discount: {get_customer_by_id(2)}")

    print("\n=== Deleting Customer ===")
    delete_customer(1)
    print("Deleted customer with ID 1")

    print("\n=== Final Customers List ===")
    for customer in get_all_customers():
        print(customer)
def quick_test():
    # Create a customer
    customer = create_customer(name="Jane Doe", email="jane@example.com", phone="1234567890")
    print("Created Customer:", customer)

    # Create a sale for that customer
    sale = create_sale(customer.id, [
        {"product_id": 1, "name": "Bread", "quantity": 1, "price_at_sale": 20},
        {"product_id": 2, "name": "Butter", "quantity": 2, "price_at_sale": 15}
    ])
    print("Created Sale:", sale)

    # Fetch purchases by customer
    purchases = get_purchases_by_customer(customer.id)
    if purchases:
        print(f"Purchases for Customer {customer.name}:")
        for sale in purchases:
            print(f"Sale ID: {sale.id}, Total: {sale.total_amount}, Date: {sale.timestamp}")
            for item in sale.items:
                print(f" - {item.name}, Qty: {item.quantity}, Price: {item.price_at_sale}")
    else:
        print("No purchases found or customer does not exist.")


if __name__ == "__main__":
    run_tests()
