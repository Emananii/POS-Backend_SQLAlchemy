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


if __name__ == "__main__":
    run_tests()
