import click
from datetime import datetime
from tabulate import tabulate
from app.db.engine import SessionLocal  # Import your session factory here
from app.services.customer_service import (
    create_customer,
    get_customer_by_id,
    get_customer_by_email,
    get_all_customers,
    update_customer,
    soft_delete_customer,
    add_loyalty_points,
    apply_discount,
    get_purchases_by_customer,
)
from app.services.reporting_service import (
    total_sales_per_customer,
    top_customers_by_sales,
    customer_purchase_frequency,
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

def handle_create(db):
    try:
        click.echo("Creating a new customer...")
        name = click.prompt("Name")
        email = click.prompt("Email")
        phone = click.prompt("Phone", default="", show_default=False)
        customer_type = click.prompt("Customer Type", type=click.Choice(["individual", "corporate"]), default="individual")
        company = click.prompt("Company Name", default="", show_default=False)
        discount = click.prompt("Discount Rate", type=float, default=0)
        customer = create_customer(db, name, email, phone, customer_type, company, discount)
        click.echo(f"✅ Created customer: {customer.name} ({customer.customer_type})")
    except Exception as e:
        click.echo(f"❌ Failed to create customer: {e}")


def handle_list(db):
    try:
        customers = get_all_customers(db)
        if not customers:
            click.echo("No customers found.")
            return

        headers = ["ID", "Name", "Email", "Phone"]

        rows = []
        for c in customers:
            rows.append([
                c.id,
                c.name,
                c.email,
                c.phone if c.phone else "-",
            ])

        table = tabulate(rows, headers=headers, tablefmt="fancy_grid")
        click.echo(table)

    except Exception as e:
        click.echo(f"Error retrieving customers: {e}")


from tabulate import tabulate

def handle_view(db):
    try:
        click.secho("🔍 Customer Directory", fg="cyan", bold=True)

        # Step 1: Fetch and display all customers in a table
        customers = get_all_customers(db)
        if not customers:
            click.echo("No customers found.")
            return

        headers = ["ID", "Name", "Email", "Type"]
        rows = [
            [c.id, c.name, c.email, c.customer_type] for c in customers
        ]
        click.echo(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

        selection = click.prompt(
            "Enter Customer ID or Name (partial or full) to view details"
        ).strip()

        customer = None
        matches = []

        if selection.isdigit():

            customer = get_customer_by_id(db, int(selection))
            if not customer:
                click.secho(f"❌ No customer found with ID {selection}", fg="red")
                return
        else:
            
            matches = [
                c for c in customers if selection.lower() in c.name.lower()
            ]

            if not matches:
                click.secho(f"❌ No customers found matching name '{selection}'", fg="red")
                return
            elif len(matches) == 1:
                customer = matches[0]
            else:
                
                click.secho(
                    f"⚠️ Multiple customers found matching '{selection}':",
                    fg="yellow",
                    bold=True,
                )
                match_rows = [[c.id, c.name, c.email, c.customer_type] for c in matches]
                click.echo(tabulate(match_rows, headers=headers, tablefmt="grid"))
                chosen_id = click.prompt("Enter exact Customer ID to view details", type=int)
                customer = get_customer_by_id(db, chosen_id)
                if not customer:
                    click.secho(f"❌ No customer found with ID {chosen_id}", fg="red")
                    return

        customer_data = [
            ["Name", customer.name],
            ["Email", customer.email],
            ["Phone", customer.phone if customer.phone else "-"],
            ["Type", customer.customer_type],
        ]

        if customer.customer_type == "business" and getattr(customer, "company_name", None):
            customer_data.append(["Company", customer.company_name])

        customer_data.extend([
            ["Loyalty Points", customer.loyalty_points],
            ["Discount Rate", f"{customer.discount_rate:.2f}%"]
        ])

        click.secho("\n✅ Customer Details:", fg="green", bold=True)
        click.echo(tabulate(customer_data, tablefmt="fancy_grid"))

    except Exception as e:
        click.secho(f"❌ Failed to retrieve customer details: {e}", fg="red")


from tabulate import tabulate

from tabulate import tabulate

def handle_update(db):
    try:
        customers = get_all_customers(db)
        if not customers:
            click.echo("No customers found.")
            return

        headers = ["ID", "Name"]
        rows = [[c.id, c.name] for c in customers]
        click.secho("📋 Customer List:", fg="cyan", bold=True)
        click.echo(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

        id_ = click.prompt("Enter the Customer ID you want to update", type=int)

        customer = get_customer_by_id(db, id_)
        if not customer:
            click.secho(f"❌ No customer found with ID {id_}", fg="red")
            return

        update_fields = [
            ("name", "Name", str),
            ("phone", "Phone", str),
            ("discount_rate", "Discount Rate (%)", float),
        ]

        updates = {}

        while True:
            click.secho("\nWhat would you like to update?", fg="cyan", bold=True)

            for i, (_, label, _) in enumerate(update_fields, start=1):
                click.echo(f"{i}. {label}")

            click.echo(f"{len(update_fields) + 1}. Finish updating")

            choice = click.prompt("Select option number", type=int)

            if choice == len(update_fields) + 1:
                break

            if choice < 1 or choice > len(update_fields):
                click.secho("⚠️ Invalid choice. Please select a valid option.", fg="yellow")
                continue

            field_key, field_label, field_type = update_fields[choice - 1]

            current_value = getattr(customer, field_key, None)


            click.echo(f"Current {field_label}: {current_value}")

            new_value = click.prompt(f"Enter new {field_label}", type=field_type)

            updates[field_key] = new_value
            click.secho(f"✅ {field_label} set to '{new_value}'", fg="green")

            if not click.confirm("Update something else?"):
                break

        if not updates:
            click.echo("No updates provided. Exiting.")
            return

        updated_customer = update_customer(db, id_, **updates)

        click.secho(f"🛠️ Successfully updated customer '{updated_customer.name}'!", fg="green", bold=True)

    except Exception as e:
        click.secho(f"❌ Failed to update customer: {e}", fg="red")

from tabulate import tabulate

def handle_delete(db):
    try:
        customers = get_all_customers(db)
        if not customers:
            click.echo("No active customers found.")
            return

        headers = ["ID", "Name"]
        rows = [[c.id, c.name] for c in customers]
        click.secho("📋 Customer List:", fg="cyan", bold=True)
        click.echo(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

        id_ = click.prompt("Enter the Customer ID you want to delete", type=int)

        customer = get_customer_by_id(db, id_)
        if not customer or customer.is_deleted:
            click.secho(f"❌ No active customer found with ID {id_}", fg="red")
            return

        confirm_msg = f"⚠️ Are you sure you want to delete customer '{customer.name}'?"
        if not click.confirm(confirm_msg):
            click.echo("❌ Deletion cancelled.")
            return

        soft_delete_customer(db, id_)
        click.secho(f"🗑️ Marked customer '{customer.name}' (ID {id_}) as deleted.", fg="green")

    except Exception as e:
        click.secho(f"❌ Failed to delete customer: {e}", fg="red")


def handle_loyalty(db):
    try:
        id_ = click.prompt("Customer ID", type=int)
        points = click.prompt("Points to add", type=int)
        customer = add_loyalty_points(db, id_, points)
        click.echo(f"🎁 Added {points} points. Total: {customer.loyalty_points}")
    except Exception as e:
        click.echo(f"❌ Failed to add loyalty points: {e}")

def handle_discount(db):
    try:
        id_ = click.prompt("Customer ID", type=int)
        discount = click.prompt("Discount to apply", type=float)
        customer = apply_discount(db, id_, discount)
        click.echo(f"💸 Applied {discount}% discount to {customer.name}")
    except Exception as e:
        click.echo(f"❌ Failed to apply discount: {e}")

def handle_purchases(db):
    try:
        id_ = click.prompt("Customer ID", type=int)
        sales = get_purchases_by_customer(db, id_)
        if not sales:
            click.echo("No purchases found.")
            return
        for sale in sales:
            click.echo(f"🧾 Sale #{sale.id} - {sale.total_amount} on {sale.timestamp}")
    except Exception as e:
        click.echo(f"❌ Failed to fetch purchases: {e}")

def handle_top_customers(db):
    try:
        limit = click.prompt("Limit number of sales", type=int, default=5)
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        data = top_customers_by_sales(db, limit, start, end)
        if not data:
            click.echo("No top customers found.")
        for d in data:
            click.echo(f"{d['customer_name']} - Ksh {d['total_sales']}")
    except Exception as e:
        click.echo(f"❌ Failed to retrieve top customers: {e}")

def handle_total_sales(db):
    try:
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        data = total_sales_per_customer(db, start, end)
        if not data:
            click.echo("No sales data found.")
        for d in data:
            click.echo(f"{d['customer_name']}: Ksh {d['total_sales']}")
    except Exception as e:
        click.echo(f"❌ Failed to get total sales: {e}")

def handle_frequency(db):
    try:
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        data = customer_purchase_frequency(db, start, end)
        if not data:
            click.echo("No purchase frequency data found.")
        for d in data:
            click.echo(f"{d['customer_name']} - {d['purchase_count']} purchases")
    except Exception as e:
        click.echo(f"❌ Failed to get purchase frequency: {e}")

@click.command()
def cli():
    db = SessionLocal()
    try:
        while True:
            try:
                choice = menu()
                if choice == 1:
                    handle_create(db)
                elif choice == 2:
                    handle_list(db)
                elif choice == 3:
                    handle_view(db)
                elif choice == 4:
                    handle_update(db)
                elif choice == 5:
                    handle_delete(db)
                elif choice == 6:
                    handle_loyalty(db)
                elif choice == 7:
                    handle_discount(db)
                elif choice == 8:
                    handle_purchases(db)
                elif choice == 9:
                    handle_top_customers(db)
                elif choice == 10:
                    handle_total_sales(db)
                elif choice == 11:
                    handle_frequency(db)
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
    finally:
        db.close()  # Make sure to close session on exit

if __name__ == "__main__":
    cli()