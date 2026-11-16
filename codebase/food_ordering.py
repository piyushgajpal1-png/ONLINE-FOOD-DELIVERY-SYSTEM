import sys

MENU = {"Burger": 120, "Pizza": 250, "Fries": 80, "Coke": 40}
VALID_COUPON = "SAVE10"
DISCOUNT_RATE = 0.10
GST_RATE = 0.05
DELIVERY_CHARGE = 40
FREE_DELIVERY_MIN = 300


def find_item(name):
    name = name.strip().lower()
    for item in MENU:
        if item.lower() == name:
            return item
    return None


def parse_quantity(text):
    text = str(text).strip()
    if not text.isdigit():
        return None
    qty = int(text)
    return qty if qty > 0 else None


def fmt(amount):
    return str(int(amount)) if float(amount).is_integer() else f"{amount:.2f}"


def find_in_cart(cart, item):
    for entry in cart:
        if entry[0] == item:
            return entry
    return None


def show_menu():
    print("\n----------- MENU -----------")
    for item, price in MENU.items():
        print(f"  {item:<8} Rs.{price}")
    print("----------------------------")


def cart_subtotal(cart):
    return sum(MENU[item] * qty for item, qty in cart)


def add_item(cart, name, quantity):
    item = find_item(name)
    if item is None:
        return "Item not available. Menu: " + ", ".join(MENU)
    qty = parse_quantity(quantity)
    if qty is None:
        return "Invalid quantity. Enter a whole number greater than 0."
    entry = find_in_cart(cart, item)
    if entry:
        entry[1] += qty
    else:
        cart.append([item, qty])
    return f"{item} x{qty} added to cart | Cart subtotal: {fmt(cart_subtotal(cart))}"


def remove_item(cart, name, quantity=None):
    item = find_item(name)
    if item is None:
        return "Item not available. Menu: " + ", ".join(MENU)
    entry = find_in_cart(cart, item)
    if entry is None:
        return f"{item} is not in your cart."
    if quantity is None or str(quantity).strip() == "":
        qty = entry[1]
    else:
        qty = parse_quantity(quantity)
        if qty is None:
            return "Invalid quantity. Enter a whole number greater than 0."
    if qty >= entry[1]:
        cart.remove(entry)
        return f"{item} removed from cart | Cart subtotal: {fmt(cart_subtotal(cart))}"
    entry[1] -= qty
    return f"{item} x{qty} removed from cart | Cart subtotal: {fmt(cart_subtotal(cart))}"


def apply_coupon(code):
    code = code.strip().upper()
    if code == VALID_COUPON:
        return code, "Coupon SAVE10 applied: 10% off the subtotal."
    return None, "Invalid coupon code. Only SAVE10 is accepted."


def calculate_bill(cart, coupon=None):
    subtotal = cart_subtotal(cart)
    discount = subtotal * DISCOUNT_RATE if coupon == VALID_COUPON else 0.0
    gst = (subtotal - discount) * GST_RATE
    delivery = 0 if subtotal >= FREE_DELIVERY_MIN else DELIVERY_CHARGE
    total = subtotal - discount + gst + delivery
    return {
        "subtotal": subtotal,
        "discount": round(discount, 2),
        "gst": round(gst, 2),
        "delivery": delivery,
        "total": round(total, 2),
    }


def checkout(cart, coupon=None):
    if not cart:
        print("Your cart is empty. Add items before checkout.")
        return False
    bill = calculate_bill(cart, coupon)
    delivery_txt = "0 (free)" if bill["delivery"] == 0 else str(bill["delivery"])
    disc_label = "Discount (10%)" if coupon else "Discount"
    print(f"Subtotal: {fmt(bill['subtotal'])} | {disc_label}: {bill['discount']:.2f}")
    print(f"GST (5%): {bill['gst']:.2f} | Delivery: {delivery_txt}")
    print(f"Total: {bill['total']:.2f}")
    return True


def view_cart(cart, coupon=None):
    if not cart:
        print("Your cart is empty.")
        return
    print("\n--- Your Cart ---")
    for item, qty in cart:
        print(f"  {item:<8} x{qty:<3} Rs.{MENU[item] * qty}")
    print(f"Cart subtotal: {fmt(cart_subtotal(cart))}")
    if coupon:
        print(f"Coupon applied: {coupon}")


def main():
    cart = []
    coupon = None
    print("Welcome to the Online Food Ordering System!")
    while True:
        print("\n1. View menu\n2. Add item\n3. Remove item\n4. View cart"
              "\n5. Apply coupon\n6. Checkout\n7. Exit")
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            show_menu()
        elif choice == "2":
            name = input("Add to cart: ")
            if find_item(name) is None:
                print("Item not available. Menu: " + ", ".join(MENU))
                continue
            print(add_item(cart, name, input("Quantity: ")))
        elif choice == "3":
            name = input("Remove from cart: ")
            qty = input("Quantity to remove (blank = all): ")
            print(remove_item(cart, name, qty))
        elif choice == "4":
            view_cart(cart, coupon)
        elif choice == "5":
            code, msg = apply_coupon(input("Coupon code: "))
            if code:
                coupon = code
            print(msg)
        elif choice == "6":
            if checkout(cart, coupon):
                cart.clear()
                coupon = None
        elif choice == "7":
            print("Thank you for ordering. Goodbye!")
            break
        else:
            print("Invalid option. Please enter a number from 1 to 7.")


def run_tests():
    print("Test Case 1: Normal input")
    cart = []
    out = add_item(cart, "Burger", 2)
    print(out)
    assert out == "Burger x2 added to cart | Cart subtotal: 240"

    print("\nTest Case 2: Boundary / minimum input")
    cart = []
    add_item(cart, "Fries", 1)
    bill = calculate_bill(cart)
    checkout(cart)
    assert bill == {"subtotal": 80, "discount": 0.0, "gst": 4.0,
                    "delivery": 40, "total": 124.0}

    print("\nTest Case 3: Invalid input")
    out_a = add_item([], "Sushi", 1)
    code, out_b = apply_coupon("FREE50")
    print(out_a)
    print(out_b)
    assert out_a == "Item not available. Menu: Burger, Pizza, Fries, Coke"
    assert code is None
    assert out_b == "Invalid coupon code. Only SAVE10 is accepted."

    print("\nTest Case 4: Different valid scenario")
    cart = []
    add_item(cart, "Pizza", 2)
    add_item(cart, "Fries", 1)
    code, _ = apply_coupon("SAVE10")
    bill = calculate_bill(cart, code)
    checkout(cart, code)
    assert bill == {"subtotal": 580, "discount": 58.0, "gst": 26.1,
                    "delivery": 0, "total": 548.1}

    print("\nAll 4 test cases passed.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        main()
