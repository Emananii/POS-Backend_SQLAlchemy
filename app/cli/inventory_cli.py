import click
from app.models.category import Category
from app.services.inventory_service import (
    create_product,
    update_product,
    purchase_product,
    get_product_by_id,
    get_all_products,
    create_category,
    update_category,
    search_products_by_name,
    get_products_by_category,
    get_products_in_stock,
    delete_product,
    get_or_create_category_by_name,  
    purchase_product as purchase_stock  
)
from app.db.engine import SessionLocal
from tabulate import tabulate


def get_db():
    """Provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_product_cli():
    """Add a new product to the inventory."""
    click.echo("\n--- Add New Product ---")
    name = click.prompt('Enter product name')
    brand = click.prompt('Enter product brand')
    purchase_price = click.prompt('Enter purchase price', type=float)
    selling_price = click.prompt('Enter selling price', type=float)
    stock = click.prompt('Enter opening stock', type=int)
    barcode = click.prompt('Enter barcode')
    category_id = click.prompt('Enter category ID', type=int)
    unit = click.prompt('Enter unit of measurement')

    db = next(get_db())
    try:
        product = create_product(
            db,
            name=name,
            brand=brand,
            purchase_price=purchase_price,
            selling_price=selling_price,
            stock=stock,
            barcode=barcode,
            category_id=category_id,
            unit=unit
        )
        click.echo(f"Product '{product.name}' added successfully with ID: {product.id}.")
    except Exception as e:
        click.echo(f"Error adding product: {e}")


def update_product_cli():
    click.echo("\n--- Update Product ---")
    product_id = click.prompt('Enter product ID to update', type=int)
    db = next(get_db())
    product = get_product_by_id(db, product_id)

    if not product:
        click.echo(f"Product with ID {product_id} not found.")
        return

    click.echo(f"Current details for Product ID {product_id}:")
    click.echo(f"  Name: {product.name}")
    click.echo(f"  Brand: {product.brand}")
    click.echo(f"  Purchase Price: {product.purchase_price}")
    click.echo(f"  Selling Price: {product.selling_price}")
    click.echo(f"  Stock: {product.stock}")
    click.echo(f"  Barcode: {product.barcode}")
    click.echo(f"  Category ID: {product.category_id}")
    click.echo(f"  Unit: {product.unit}")

    name = click.prompt(f'Enter new name (current: {product.name})', default=product.name)
    brand = click.prompt(f'Enter new brand (current: {product.brand})', default=product.brand)
    purchase_price = click.prompt(f'Enter new purchase price (current: {product.purchase_price})', default=product.purchase_price, type=float)
    selling_price = click.prompt(f'Enter new selling price (current: {product.selling_price})', default=product.selling_price, type=float)
    stock = click.prompt(f'Enter new stock quantity (current: {product.stock})', default=product.stock, type=int)

    if product.barcode:
        barcode = click.prompt(f'Enter new barcode (current: {product.barcode})', default=product.barcode)
    else:
        barcode = click.prompt('Enter barcode (or leave blank to skip)', default='', show_default=False)

    use_category = click.confirm("Would you like to update or assign a category?")
    category_id = product.category_id
    if use_category:
        category_name = click.prompt('Enter category name (existing or new)')
        try:
            category = get_or_create_category_by_name(db, category_name)
            category_id = category.id
            click.echo(f"Using category '{category.name}' with ID {category.id}")
        except Exception as e:
            click.echo(f"Error handling category: {e}")
            category_id = None  

    unit = click.prompt(f'Enter new unit (current: {product.unit})', default=product.unit)

    try:
        updated_product = update_product(
            db,
            product_id=product_id,
            name=name,
            brand=brand,
            purchase_price=purchase_price,
            selling_price=selling_price,
            stock=stock,
            barcode=barcode if barcode else None,
            category_id=category_id,
            unit=unit
        )
        click.echo(f"✅ Product '{updated_product.name}' updated successfully.")
    except Exception as e:
        click.echo(f"❌ Error updating product: {e}")


def list_products():
    """List all products in the inventory."""
    click.echo("\n--- All Products ---")
    db = next(get_db())
    products = get_all_products(db)

    if products:
        table_data = []
        headers = ["ID", "Name", "Brand", "Sell Price", "Stock", "Unit", "Category ID", "Barcode", "Image"]

        for product in products:
            table_data.append([
                product.id,
                product.name,
                product.brand,
                f"${product.selling_price:.2f}",
                product.stock,
                product.unit,
                product.category_id,
                product.barcode,
                product.image if product.image else "-"
            ])

        click.echo(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    else:
        click.echo("No products found in the inventory.")

def purchase_stock_cli():
    """Purchase additional stock for an existing product."""
    click.echo("\n--- Purchase Stock ---")
    db = next(get_db())

    try:
        product_id = click.prompt("Enter product ID to restock", type=int)
        quantity = click.prompt("Enter quantity to purchase", type=int)
        new_purchase_price = click.prompt("Enter new purchase price per unit (ksh)", type=float)
        new_selling_price = click.prompt("Enter new selling price per unit (ksh)", type=float)  

        product = get_product_by_id(db, product_id)
        if not product:
            click.echo(f"Product with ID {product_id} not found.")
            return

        updated_product = purchase_stock(db, product_id, new_purchase_price, new_selling_price, quantity)
        click.echo(
            f"✅ Purchased {quantity} units of '{updated_product.name}'. "
            f"New stock: {updated_product.stock}, "
            f"Updated purchase price: ksh{updated_product.purchase_price:.2f}, "
            f"Updated selling price: ksh{updated_product.selling_price:.2f}"  
        )
    except Exception as e:
        click.echo(f"❌ Error purchasing stock: {e}")


def create_category_cli():
    """Create a new product category."""
    click.echo("\n--- Create New Category ---")
    name = click.prompt('Enter category name')
    db = next(get_db())
    try:
        category = create_category(db, name=name)
        click.echo(f"Category '{category.name}' created successfully with ID: {category.id}.")
    except Exception as e:
        click.echo(f"Error creating category: {e}")


def update_category_cli():
    """Update category details."""
    click.echo("\n--- Update Category ---")
    category_id = click.prompt('Enter category ID to update', type=int)
    name = click.prompt('Enter new category name')
    db = next(get_db())
    try:
        updated_category = update_category(db, category_id=category_id, name=name)
        if updated_category:
            click.echo(f"Category ID {category_id} updated to '{updated_category.name}' successfully.")
        else:
            click.echo(f"Category with ID {category_id} not found.")
    except Exception as e:
        click.echo(f"Error updating category: {e}")


def search_product_by_name(name_query):
    """Search for products by name."""
    click.echo(f"\n--- Searching for products with name '{name_query}' ---")
    db = next(get_db())
    products = search_products_by_name(db, name_query)
    if products:
        for product in products:
            click.echo(f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, "
                       f"Price: ${product.selling_price:.2f}, Stock: {product.stock} {product.unit}")
    else:
        click.echo(f"No products found matching '{name_query}'.")


def list_products_by_category(category_id):
    """List products belonging to a specific category."""
    click.echo(f"\n--- Products in Category ID {category_id} ---")
    db = next(get_db())
    products = get_products_by_category(db, category_id)
    if products:
        for product in products:
            click.echo(f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, "
                       f"Price: ${product.selling_price:.2f}, Stock: {product.stock} {product.unit}")
    else:
        click.echo(f"No products found for category ID {category_id}.")


def view_product_stock_levels():
    """View stock levels for all products."""
    click.echo("\n--- Product Stock Levels ---")
    db = next(get_db())
    products = get_products_in_stock(db)
    if products:
        for product in products:
            click.echo(f"ID: {product.id}, Name: {product.name}, Stock: {product.stock} {product.unit}")
    else:
        click.echo("No products with stock information found.")


def delete_product_cli():
    """Delete a product from the inventory."""
    click.echo("\n--- Delete Product ---")
    product_id = click.prompt('Enter product ID to delete', type=int)
    db = next(get_db())

    
    from app.models.sale_item import SaleItem
    from app.models.product import Product  
    
    try:
    
        sale_items = db.query(SaleItem).filter(SaleItem.product_id == product_id).all()
        
        if sale_items:
            click.echo(f"Product has {len(sale_items)} linked sale items.")
            
            for sale_item in sale_items:
                db.delete(sale_item)  
                click.echo(f"Deleted sale item with ID {sale_item.id}.")
            db.commit()  
        else:
            click.echo("No sale items found for this product.")
        
        
        product = db.query(Product).filter(Product.id == product_id).first()  
        if product:
            db.delete(product) 
            db.commit()  
            click.echo(f"Product with ID {product_id} deleted successfully.")
        else:
            click.echo(f"Product with ID {product_id} not found.")
    except Exception as e:
        db.rollback()  
        click.echo(f"Error deleting product: {e}")


def inventory_menu():
    """Displays the main inventory CLI menu options."""
    click.echo("\n🧾 INVENTORY CLI MENU")
    click.echo("1. Add a new product")
    click.echo("2. Update a product")
    click.echo("3. List all products")
    click.echo("4. Create a new category")
    click.echo("5. Update a category")
    click.echo("6. Search for a product by name")
    click.echo("7. List products by category")
    click.echo("8. View product stock levels")
    click.echo("9. Delete a product")
    click.echo("10. Purchase stock")
    click.echo("11. Exit")


@click.command()
def menu():
    """Main menu for inventory management."""
    while True:
        inventory_menu()
        try:
            choice = click.prompt("Enter a number", type=int)
        except click.Abort:
            click.echo("\nExiting due to user interruption.")
            break
        except ValueError:
            click.echo("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            add_product_cli()
        elif choice == 2:
            update_product_cli()
        elif choice == 3:
            list_products()
        elif choice == 4:
            create_category_cli()
        elif choice == 5:
            update_category_cli()
        elif choice == 6:
            name = click.prompt("Enter product name to search")
            search_product_by_name(name)
        elif choice == 7:
            category_id = click.prompt("Enter category ID to list products", type=int)
            list_products_by_category(category_id)
        elif choice == 8:
            view_product_stock_levels()
        elif choice == 9:
            delete_product_cli()
        elif choice == 10:
            purchase_stock_cli()
        elif choice == 11:
            click.echo("Exiting the menu...")
            break
        else:
            click.echo("Invalid option, please select a valid choice.")


if __name__ == '__main__':
    menu()
