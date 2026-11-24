
function Cart({ cart, setCart, onCheckout }) {
    const increaseQuantity = (productId) => {
        setCart((previous) =>
            previous.map((item) =>
                item.product_id === productId
                    ? { ...item, cart_quantity: item.cart_quantity + 1 }
                    : item
            )
        );
    };

    const decreaseQuantity = (productId) => {
        setCart((previous) =>
            previous
                .map((item) =>
                    item.product_id === productId
                        ? { ...item, cart_quantity: item.cart_quantity - 1 }
                        : item
                )
                .filter((item) => item.cart_quantity > 0)
        );
    };

    const removeItem = (productId) => {
        setCart((previous) =>
            previous.filter((item) => item.product_id !== productId)
        );
    };

    const total = cart.reduce(
        (sum, item) => sum + Number(item.price) * item.cart_quantity,
        0
    );

    return (
        <section className="cart-section">
            <h2>Your Shopping Cart</h2>

            {cart.length === 0 ? (
                <p>Your cart is empty.</p>
            ) : (
                <>
                    {cart.map((item) => (
                        <div className="cart-item" key={item.product_id}>
                            <div>
                                <h3>{item.name}</h3>
                                <p>€{Number(item.price).toFixed(2)}</p>
                            </div>

                            <div className="quantity-controls">
                                <button onClick={() => decreaseQuantity(item.product_id)}>
                                    -
                                </button>

                                <span>{item.cart_quantity}</span>

                                <button
                                    disabled={item.cart_quantity >= item.available_quantity}
                                    onClick={() => increaseQuantity(item.product_id)}
                                >
                                    +
                                </button>
                            </div>

                            <button
                                className="remove-button"
                                onClick={() => removeItem(item.product_id)}
                            >
                                Remove
                            </button>
                        </div>
                    ))}

                    <h3 className="cart-total">
                        Total: €{total.toFixed(2)}
                    </h3>

                    <button className="checkout-button" onClick={onCheckout}>
                        Place Order
                    </button>
                </>
            )}
        </section>
    );
}

export default Cart;
