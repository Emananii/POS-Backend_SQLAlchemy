# scripts/test_sales_service.py

from app.services.sales_service import (
    create_sale, get_all_sales, get_sale_by_id, delete_sale, get_sales_summary_by_day
)

def quick_test():
    # Create sale
    sale = create_sale(1, [
        {"product_id": 1, "name": "Milk", "quantity": 2, "price_at_sale": 50},
        {"product_id": 2, "name": "Eggs", "quantity": 1, "price_at_sale": 30}
    ])
    print("Created Sale:", sale)

    # Fetch all sales
    sales = get_all_sales()
    for s in sales:
        print("Sale:", s, "Items:", s.items)

    # Get summary
    summary = get_sales_summary_by_day()
    print("Sales Summary by Day:", summary)

if __name__ == "__main__":
    quick_test()
