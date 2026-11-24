
import { useEffect, useState } from "react";
import api from "../api/axios";

function CustomerOrders() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchOrders = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get("/orders/my-orders");
            setOrders(response.data.orders || []);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.message || "Could not load your orders."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    return (
        <section className="customer-orders">
            <div className="orders-heading">
                <div>
                    <p className="hero-label">MY ACCOUNT</p>
                    <h2>My Order History</h2>
                    <p>Track your purchases and order status.</p>
                </div>

                <button onClick={fetchOrders} className="reset-button">
                    Refresh Orders
                </button>
            </div>

            {loading && <p>Loading your orders...</p>}

            {error && <p className="error-message">{error}</p>}

            {!loading && !error && orders.length === 0 && (
                <p>You haven't placed any orders yet.</p>
            )}

            {!loading && !error && orders.map((order) => (
                <div className="customer-order-card" key={order.order_id}>
                    <div className="customer-order-header">
                        <div>
                            <h3>Order #{order.order_id}</h3>
                            <p>{order.order_date}</p>
                        </div>

                        <span className={`order-status status-${order.status}`}>
                            {order.status}
                        </span>
                    </div>

                    <div className="customer-order-products">
                        <h4>Products</h4>

                        {order.items.map((item, index) => (
                            <div
                                className="customer-order-product"
                                key={index}
                            >
                                <span>
                                    {item.product_name} × {item.quantity}
                                </span>

                                <strong>
                                    €{(item.unit_price * item.quantity).toFixed(2)}
                                </strong>
                            </div>
                        ))}
                    </div>

                    <div className="customer-order-total">
                        <span>Total</span>
                        <strong>
                            €{Number(order.total_amount).toFixed(2)}
                        </strong>
                    </div>
                </div>
            ))}
        </section>
    );
}

export default CustomerOrders;
