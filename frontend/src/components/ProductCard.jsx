
function ProductCard({ product, onAddToCart }) {
    return (
        <div className="product-card">
            <div className="product-image">
                <span>NO IMAGE</span>
            </div>

            <div className="product-info">
                <h3>{product.name}</h3>

                <p className="product-price">
                    €{Number(product.price).toFixed(2)}
                </p>

                <p className="product-stock">
                    {product.available_quantity > 0
                        ? `${product.available_quantity} available`
                        : "Out of stock"}
                </p>

                <button
                    className="add-button"
                    disabled={product.available_quantity <= 0}
                    onClick={() => onAddToCart(product)}
                >
                    Add to Cart
                </button>
            </div>
        </div>
    );
}

export default ProductCard;
