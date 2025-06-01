import click
from datetime import datetime
from app.services.customer_service import (
    create_customer,
    get_customer_by_id,
    get_customer_by_email,
    get_all_customers,
    update_customer,
    delete_customer,
    add_loyalty_points,
    apply_discount,
    get_purchases_by_customer,
)
from app.services.reporting_service import (
    total_sales_per_customer,
    top_customers_by_sales,
    customer_purchase_frequency
)

def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str) if date_str else None
    except ValueError:
        raise click.BadParameter("Invalid date format. Use YYYY-MM-DD.")

def menu():
    click.echo("\n🧾 CUSTOMER CLI MENU")
    click.echo("1. Create a new customer")
    click.echo("2. List all customers")
    click.echo("3. View customer details")
    click.echo("4. Update a customer")
    click.echo("5. Delete a customer")
    click.echo("6. Add loyalty points")
    click.echo("7. Apply discount")
    click.echo("8. View purchases")
    click.echo("9. Top customers by sales")
    click.echo("10. Total sales per customer")
    click.echo("11. Purchase frequency")
    click.echo("12. Exit")
    try:
        return click.prompt("\nEnter a number", type=int)
    except click.exceptions.Abort:
        click.echo("\nAborted. Exiting.")
        exit()

def handle_create():
    try:
        click.echo("Creating a new customer...")
        name = click.prompt("Name")
        email = click.prompt("Email")
        phone = click.prompt("Phone", default="", show_default=False)
        customer_type = click.prompt("Customer Type", type=click.Choice(["individual", "corporate"]), default="individual")
        company = click.prompt("Company Name", default="", show_default=False)
        discount = click.prompt("Discount Rate", type=float, default=0)
        customer = create_customer(name, email, phone, customer_type, company, discount)
        click.echo(f"✅ Created customer: {customer.name} ({customer.customer_type})")
    except Exception as e:
        click.echo(f"❌ Failed to create customer: {e}")

def handle_list():
    try:
        customers = get_all_customers()
        if not customers:
            click.echo("No customers found.")
        for c in customers:
            click.echo(f"{c.id}: {c.name} ({c.email}) - {c.customer_type}")
    except Exception as e:
        click.echo(f"❌ Error retrieving customers: {e}")

def handle_view():
    try:
        click.echo("🔍 View Customer Details")
        click.echo("   You can search by:")
        click.echo("     1. ID")
        click.echo("     2. Email")

        # Flexible prompt input mapping
        valid_inputs = {
            "1": "id",
            "id": "id",
            "2": "email",
            "email": "email"
        }

        # Prompt in a loop until valid input is given
        while True:
            raw_input = click.prompt("Enter search method (1 for ID, 2 for Email)").strip().lower()
            search_method = valid_inputs.get(raw_input)
            if search_method:
                break
            click.secho("⚠️ Invalid input. Please type '1', '2', 'id', or 'email'.", fg="yellow")

        # Fetch customer based on method
        if search_method == "id":
            id_ = click.prompt("🔢 Enter Customer ID", type=int)
            customer = get_customer_by_id(id_)
        else:
            email = click.prompt("📧 Enter Customer Email").strip()
            customer = get_customer_by_email(email)

        # Display result
        if not customer:
            click.secho("❌ No customer found with the provided information.", fg="red")
        else:
            click.secho("✅ Customer Found:", fg="green", bold=True)
            click.echo(f"   👤 Name        : {customer.name}")
            click.echo(f"   📧 Email       : {customer.email}")
            click.echo(f"   📱 Phone       : {customer.phone}")
            click.echo(f"   🏷️ Type        : {customer.customer_type}")
            if customer.customer_type == "business" and customer.company_name:
                click.echo(f"   🏢 Company     : {customer.company_name}")
            click.echo(f"   ⭐ Loyalty Pts : {customer.loyalty_points}")
            click.echo(f"   💸 Discount    : {customer.discount_rate:.2f}%")

    except Exception as e:
        click.secho(f"❌ Failed to retrieve customer details: {e}", fg="red")


def handle_update():
    try:
        id_ = click.prompt("Customer ID", type=int)
        updates = {}
        if click.confirm("Update name?"):
            updates["name"] = click.prompt("New name")
        if click.confirm("Update phone?"):
            updates["phone"] = click.prompt("New phone")
        if click.confirm("Update discount?"):
            updates["discount_rate"] = click.prompt("New discount rate", type=float)
        if not updates:
            click.echo("No updates provided.")
            return
        customer = update_customer(id_, **updates)
        click.echo(f"🛠️ Updated customer: {customer.name}")
    except Exception as e:
        click.echo(f"❌ Failed to update customer: {e}")

def handle_delete():
    try:
        id_ = click.prompt("Customer ID", type=int)
        delete_customer(id_)
        click.echo(f"❌ Deleted customer with ID {id_}")
    except Exception as e:
        click.echo(f"❌ Failed to delete customer: {e}")

def handle_loyalty():
    try:
        id_ = click.prompt("Customer ID", type=int)
        points = click.prompt("Points to add", type=int)
        customer = add_loyalty_points(id_, points)
        click.echo(f"🎁 Added {points} points. Total: {customer.loyalty_points}")
    except Exception as e:
        click.echo(f"❌ Failed to add loyalty points: {e}")

def handle_discount():
    try:
        id_ = click.prompt("Customer ID", type=int)
        discount = click.prompt("Discount to apply", type=float)
        customer = apply_discount(id_, discount)
        click.echo(f"💸 Applied {discount}% discount to {customer.name}")
    except Exception as e:
        click.echo(f"❌ Failed to apply discount: {e}")

def handle_purchases():
    try:
        id_ = click.prompt("Customer ID", type=int)
        sales = get_purchases_by_customer(id_)
        if not sales:
            click.echo("No purchases found.")
            return
        for sale in sales:
            click.echo(f"🧾 Sale #{sale.id} - {sale.total_amount} on {sale.timestamp}")
    except Exception as e:
        click.echo(f"❌ Failed to fetch purchases: {e}")

def handle_top_customers():
    try:
        limit = click.prompt("Limit number of sales", type=int, default=5)
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        data = top_customers_by_sales(limit, start, end)
        if not data:
            click.echo("No top customers found.")
        for d in data:
            click.echo(f"{d['customer_name']} - Ksh {d['total_sales']}")
    except Exception as e:
        click.echo(f"❌ Failed to retrieve top customers: {e}")

def handle_total_sales():
    try:
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        data = total_sales_per_customer(start, end)
        if not data:
            click.echo("No sales data found.")
        for d in data:
            click.echo(f"{d['customer_name']}: Ksh {d['total_sales']}")
    except Exception as e:
        click.echo(f"❌ Failed to get total sales: {e}")

def handle_frequency():
    try:
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        data = customer_purchase_frequency(start, end)
        if not data:
            click.echo("No purchase frequency data found.")
        for d in data:
            click.echo(f"{d['customer_name']} - {d['purchase_count']} purchases")
    except Exception as e:
        click.echo(f"❌ Failed to get purchase frequency: {e}")

@click.command()
def cli():
    while True:
        try:
            choice = menu()
            if choice == 1: handle_create()
            elif choice == 2: handle_list()
            elif choice == 3: handle_view()
            elif choice == 4: handle_update()
            elif choice == 5: handle_delete()
            elif choice == 6: handle_loyalty()
            elif choice == 7: handle_discount()
            elif choice == 8: handle_purchases()
            elif choice == 9: handle_top_customers()
            elif choice == 10: handle_total_sales()
            elif choice == 11: handle_frequency()
            elif choice == 12:
                click.echo("Goodbye! 👋")
                break
            else:
                click.echo("Invalid option. Please try again.")
        except click.exceptions.Abort:
            click.echo("\n👋 Exiting...")
            break
        except Exception as e:
            click.echo(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    cli()