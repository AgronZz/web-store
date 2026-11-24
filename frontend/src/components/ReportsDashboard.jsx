
import { useEffect, useState } from "react";
import api from "../api/axios";

function ReportsDashboard() {
    const [daily, setDaily] = useState(null);
    const [monthly, setMonthly] = useState(null);
    const [topProducts, setTopProducts] = useState([]);

    const today = new Date();
    const [year, setYear] = useState(today.getFullYear());
    const [month, setMonth] = useState(today.getMonth() + 1);

    const fetchReports = async () => {
        try {
            const [dailyResponse, monthlyResponse, topResponse] =
                await Promise.all([
                    api.get("/reports/daily-earnings"),
                    api.get("/reports/monthly-earnings", {
                        params: { year, month }
                    }),
                    api.get("/reports/top-products")
                ]);

            setDaily(dailyResponse.data);
            setMonthly(monthlyResponse.data);
            console.log("TOP PRODUCTS RESPONSE:", topResponse.data);

            setTopProducts(
                Array.isArray(topResponse.data.products)
                    ? topResponse.data.products
                    : []
            );
        } catch (error) {
            console.error("Reports error:", error);
        }
    };

    useEffect(() => {
        fetchReports();
    }, [year, month]);

    return (
        <section className="reports-dashboard">
            <h2>Sales Reports</h2>

            <div className="report-cards">
                <div className="report-card">
                    <h3>Daily Earnings</h3>
                    <h2>
                        €{Number(daily?.total_earnings || 0).toFixed(2)}
                    </h2>
                    <p>Orders: {daily?.total_orders || 0}</p>
                </div>

                <div className="report-card">
                    <h3>Monthly Earnings</h3>
                    <h2>
                        €{Number(monthly?.total_earnings || 0).toFixed(2)}
                    </h2>
                    <p>Orders: {monthly?.total_orders || 0}</p>
                </div>
            </div>

            <div className="report-filter">
                <label>Year:</label>
                <input
                    type="number"
                    value={year}
                    onChange={(e) => setYear(Number(e.target.value))}
                />

                <label>Month:</label>
                <select
                    value={month}
                    onChange={(e) => setMonth(Number(e.target.value))}
                >
                    {Array.from({ length: 12 }, (_, i) => (
                        <option key={i + 1} value={i + 1}>
                            {i + 1}
                        </option>
                    ))}
                </select>
            </div>

            <h3>Top-Selling Products</h3>

            {topProducts.map((product) => (
                <div className="top-product" key={product.product_id}>
                    <strong>{product.name}</strong>
                    <span>{product.total_sold} sold</span>
                    <span>
                        €{Number(product.total_revenue).toFixed(2)}
                    </span>
                </div>
            ))}
        </section>
    );
}

export default ReportsDashboard;
