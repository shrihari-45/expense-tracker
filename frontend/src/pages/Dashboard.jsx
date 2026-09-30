import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
    TrendingDown,
    TrendingUp,
    Wallet,
    PiggyBank,
    Receipt,
    Lightbulb,
    ArrowUpRight
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import api from '../services/api';
import './Dashboard.css';

const BAR_COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4'];

export default function Dashboard() {
    const [expenses, setExpenses] = useState([]);
    const [monthlyIncome] = useState(75000);
    const [insights, setInsights] = useState([]);
    const [loading, setLoading] = useState(true);

    // Requirement: useCallback for standard fetch
    const fetchDashboardData = useCallback(async () => {
        try {
            setLoading(true);
            const [expRes, insightsRes] = await Promise.allSettled([
                api.get('/expenses'),
                api.post('/ai/insights')
            ]);

            if (expRes.status === 'fulfilled') setExpenses(expRes.value.data);
            if (insightsRes.status === 'fulfilled') setInsights(insightsRes.value.data.insights || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);

    // Requirement: useMemo for high-frequency calculations
    const totalExpense = useMemo(() => {
        return expenses.reduce((acc, curr) => acc + Number(curr.amount || 0), 0);
    }, [expenses]);

    const remainingBalance = useMemo(() => {
        return monthlyIncome - totalExpense;
    }, [monthlyIncome, totalExpense]);

    const savingsRate = useMemo(() => {
        if (monthlyIncome <= 0) return 0;
        return Math.max(0, ((remainingBalance / monthlyIncome) * 100).toFixed(1));
    }, [monthlyIncome, remainingBalance]);

    const categoryAggregated = useMemo(() => {
        const map = {};
        expenses.forEach((item) => {
            map[item.category] = (map[item.category] || 0) + Number(item.amount);
        });
        return Object.entries(map).map(([name, value]) => ({ name, value }));
    }, [expenses]);

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '64px' }}>
                <p style={{ color: 'var(--text-muted)' }}>Aggregating balances and analytical reports...</p>
            </div>
        );
    }

    return (
        <div>
            <div style={{ marginBottom: '24px' }}>
                <h2 className="page-title">Executive Dashboard</h2>
                <p className="page-desc">Overview of cash inflow, expenditures, and portfolio ratios.</p>
            </div>

            <div className="metrics-grid">
                <div className="kpi-card">
                    <div>
                        <span className="kpi-label">Total Income</span>
                        <div className="kpi-value">₹{monthlyIncome.toLocaleString('en-IN')}</div>
                        <span className="kpi-subtext" style={{ color: 'var(--success)' }}>
                            Target Monthly Inflow
                        </span>
                    </div>
                    <div className="kpi-icon-box" style={{ background: 'var(--success-bg)', color: 'var(--success)' }}>
                        <Wallet size={24} />
                    </div>
                </div>

                <div className="kpi-card">
                    <div>
                        <span className="kpi-label">Total Expenses</span>
                        <div className="kpi-value">₹{totalExpense.toLocaleString('en-IN')}</div>
                        <span className="kpi-subtext" style={{ color: 'var(--danger)' }}>
                            {expenses.length} Total Logs
                        </span>
                    </div>
                    <div className="kpi-icon-box" style={{ background: 'var(--danger-bg)', color: 'var(--danger)' }}>
                        <Receipt size={24} />
                    </div>
                </div>

                <div className="kpi-card">
                    <div>
                        <span className="kpi-label">Remaining Balance</span>
                        <div className="kpi-value" style={{ color: remainingBalance >= 0 ? 'var(--text-main)' : 'var(--danger)' }}>
                            ₹{remainingBalance.toLocaleString('en-IN')}
                        </div>
                        <span className="kpi-subtext" style={{ color: 'var(--text-muted)' }}>
                            Available Buffer
                        </span>
                    </div>
                    <div className="kpi-icon-box" style={{ background: 'var(--primary-subtle)', color: 'var(--primary)' }}>
                        <PiggyBank size={24} />
                    </div>
                </div>

                <div className="kpi-card">
                    <div>
                        <span className="kpi-label">Savings Rate</span>
                        <div className="kpi-value">{savingsRate}%</div>
                        <span className="kpi-subtext" style={{ color: 'var(--primary)' }}>
                            Recommended: ≥ 30%
                        </span>
                    </div>
                    <div className="kpi-icon-box" style={{ background: 'var(--warning-bg)', color: 'var(--warning)' }}>
                        <ArrowUpRight size={24} />
                    </div>
                </div>
            </div>

            <div className="analytics-grid">
                <div className="chart-card">
                    <h3 className="chart-title">Expense Allocation by Category</h3>
                    {categoryAggregated.length === 0 ? (
                        <div style={{ height: '240px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-subtle)' }}>
                            No transactions recorded yet.
                        </div>
                    ) : (
                        <div style={{ height: '260px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={categoryAggregated}>
                                    <XAxis dataKey="name" tickLine={false} axisLine={false} />
                                    <YAxis tickLine={false} axisLine={false} />
                                    <Tooltip
                                        formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Spent']}
                                        contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
                                    />
                                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                                        {categoryAggregated.map((_, i) => (
                                            <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </div>

                <div className="chart-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                            <Lightbulb size={20} color="var(--warning)" />
                            <h3 className="chart-title" style={{ margin: 0 }}>Automated AI Insights</h3>
                        </div>

                        {insights.length > 0 ? (
                            insights.slice(0, 3).map((item, idx) => (
                                <div key={idx} className="insight-item">
                                    <strong style={{ display: 'block', marginBottom: '2px', color: item.type === 'alert' ? 'var(--danger)' : 'var(--primary)' }}>
                                        {item.type === 'alert' ? '⚠ Outlier Detected' : '💡 Efficiency Tip'}
                                    </strong>
                                    {item.message}
                                </div>
                            ))
                        ) : (
                            <div>
                                <div className="insight-item">
                                    <strong>Baseline Pattern:</strong> Add 3 or more entries to enable variance detection.
                                </div>
                                <div className="insight-item">
                                    <strong>Allocation Standard:</strong> 50/30/20 rule aligns with your targets.
                                </div>
                            </div>
                        )}
                    </div>

                    <a href="/assistant" style={{ fontSize: '0.8125rem', color: 'var(--primary)', fontWeight: '600', textDecoration: 'none' }}>
                        Open conversational agent →
                    </a>
                </div>
            </div>
        </div>
    );
}