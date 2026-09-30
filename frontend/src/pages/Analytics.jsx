import React, { useState, useEffect, useMemo } from 'react';
import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    Legend
} from 'recharts';
import api from '../services/api';

const PIE_COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#f97316', '#64748b'];

export default function Analytics() {
    const [expenses, setExpenses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        (async () => {
            try {
                const res = await api.get('/expenses');
                setExpenses(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    // Category Distribution for Doughnut
    const categoryData = useMemo(() => {
        const map = {};
        expenses.forEach((item) => {
            map[item.category] = (map[item.category] || 0) + Number(item.amount);
        });
        return Object.entries(map).map(([name, value]) => ({ name, value }));
    }, [expenses]);

    // Chronological Monthly Trend for Bar Chart
    const monthlyData = useMemo(() => {
        const map = {};
        expenses.forEach((item) => {
            const month = item.date.substring(0, 7); // YYYY-MM
            map[month] = (map[month] || 0) + Number(item.amount);
        });
        return Object.entries(map)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([month, amount]) => ({ month, amount }));
    }, [expenses]);

    // Cashflow Curve (Simulated Income vs Real Expense)
    const cashflowData = useMemo(() => {
        return monthlyData.map(item => ({
            month: item.month,
            Expenses: item.amount,
            Income: 75000 // Standard income benchmark
        }));
    }, [monthlyData]);

    if (loading) {
        return <div style={{ padding: '64px', textAlign: 'center', color: 'var(--text-muted)' }}>Rendering analytics engine...</div>;
    }

    return (
        <div style={{ spaceY: '24px' }}>
            <div style={{ marginBottom: '24px' }}>
                <h2 className="page-title">Expense Analytics</h2>
                <p className="page-desc">Visual distribution, velocity, and longitudinal cashflow patterns.</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
                {/* Doughnut Chart */}
                <div className="chart-card">
                    <h3 className="chart-title">Categorical Allocation</h3>
                    <div style={{ height: '300px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={categoryData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={65}
                                    outerRadius={105}
                                    paddingAngle={3}
                                    dataKey="value"
                                >
                                    {categoryData.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Total']} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Monthly Bar Chart */}
                <div className="chart-card">
                    <h3 className="chart-title">Monthly Expense Volume</h3>
                    <div style={{ height: '300px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={monthlyData}>
                                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                                <YAxis tickLine={false} axisLine={false} />
                                <Tooltip formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Spent']} />
                                <Bar dataKey="amount" fill="var(--primary)" radius={[6, 6, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Income vs Expense Line Chart */}
            <div className="chart-card" style={{ marginTop: '20px' }}>
                <h3 className="chart-title">Cash Flow: Income vs Expenses</h3>
                <div style={{ height: '320px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={cashflowData}>
                            <XAxis dataKey="month" tickLine={false} axisLine={false} />
                            <YAxis tickLine={false} axisLine={false} />
                            <Tooltip formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`]} />
                            <Legend />
                            <Line type="monotone" dataKey="Income" stroke="var(--success)" strokeWidth={2.5} dot={{ r: 4 }} />
                            <Line type="monotone" dataKey="Expenses" stroke="var(--danger)" strokeWidth={2.5} dot={{ r: 4 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}