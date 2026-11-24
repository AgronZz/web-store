
function Navbar({ cartCount, onCartClick }) {
    return (
        <nav className="navbar">
            <div className="logo">
                URBAN<span>STORE</span>
            </div>

            <div className="nav-links">
                <a href="/">Home</a>
                <a href="#products">Shop</a>
                <a href="#categories">Categories</a>
            </div>

            <div className="nav-actions">
                <button className="cart-button" onClick={onCartClick}>
                    🛒 Cart ({cartCount})
                </button>
            </div>
        </nav>
    );
}

export default Navbar;
