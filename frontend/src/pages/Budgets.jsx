import React, { useState, useEffect, useMemo } from 'react';
import { PiggyBank, Plus, AlertTriangle, CheckCircle2 } from 'lucide-react';
import api from '../services/api';

const DEFAULT_BUDGETS = [
    { id: 1, category: 'Food', limit: 7000 },
    { id: 2, category: 'Shopping', limit: 5000 },
    { id: 3, category: 'Transport', limit: 3000 },
    { id: 4, category: 'Entertainment', limit: 2000 },
];

export default function Budgets() {
    const [budgets, setBudgets] = useState(DEFAULT_BUDGETS);
    const [expenses, setExpenses] = useState([]);
    const [loading, setLoading] = useState(true);

    // New budget state
    const [category, setCategory] = useState('Groceries');
    const [limit, setLimit] = useState('');

    useEffect(() => {
        (async () => {
            try {
                const [bRes, expRes] = await Promise.allSettled([
                    api.get('/budgets'),
                    api.get('/expenses')
                ]);
                if (bRes.status === 'fulfilled' && bRes.value.data.length > 0) {
                    setBudgets(bRes.value.data);
                }
                if (expRes.status === 'fulfilled') {
                    setExpenses(expRes.value.data);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    // Compute category spending
    const spendingMap = useMemo(() => {
        const map = {};
        expenses.forEach((item) => {
            map[item.category] = (map[item.category] || 0) + Number(item.amount);
        });
        return map;
    }, [expenses]);

    const handleAddBudget = async (e) => {
        e.preventDefault();
        if (!limit || Number(limit) <= 0) return;

        const newEntry = { category, limit: parseFloat(limit) };
        try {
            const res = await api.post('/budgets', newEntry);
            setBudgets(prev => [...prev, res.data]);
        } catch {
            // Local fallback
            setBudgets(prev => [...prev, { ...newEntry, id: Date.now() }]);
        }
        setLimit('');
    };

    return (
        <div>
            <div style={{ marginBottom: '24px' }}>
                <h2 className="page-title">Budget Allocation & Guardrails</h2>
                <p className="page-desc">Define category ceiling thresholds with real-time overrun detection.</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
                {/* New Budget Allocation Form */}
                <div className="form-card" style={{ margin: 0, height: 'fit-content' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>Set Category Limit</h3>
                    <form onSubmit={handleAddBudget}>
                        <div className="form-group">
                            <label className="form-label">Category</label>
                            <select
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                                className="form-control"
                            >
                                {['Food', 'Shopping', 'Transport', 'Bills', 'Entertainment', 'Health', 'Education', 'Travel', 'Groceries', 'Other'].map(c => (
                                    <option key={c} value={c}>{c}</option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Monthly Limit (₹)</label>
                            <input
                                type="number"
                                required
                                placeholder="5000"
                                value={limit}
                                onChange={(e) => setLimit(e.target.value)}
                                className="form-control"
                            />
                        </div>

                        <button type="submit" className="btn-submit" style={{ marginTop: '12px' }}>
                            <Plus size={16} />
                            Commit Budget
                        </button>
                    </form>
                </div>

                {/* Budget Progress Tiles */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {budgets.map((b) => {
                        const spent = spendingMap[b.category] || 0;
                        const percent = Math.min(Math.round((spent / b.limit) * 100), 100);
                        const isExceeded = spent > b.limit;

                        return (
                            <div
                                key={b.id || b.category}
                                className="kpi-card"
                                style={{ flexDirection: 'column', alignItems: 'stretch', gap: '12px' }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>{b.category}</h4>
                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            ₹{spent.toLocaleString('en-IN')} of ₹{b.limit.toLocaleString('en-IN')} allocated
                                        </span>
                                    </div>
                                    {isExceeded ? (
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--danger)', fontSize: '0.75rem', fontWeight: 700 }}>
                                            <AlertTriangle size={16} /> Budget Exceeded
                                        </div>
                                    ) : (
                                        <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--text-main)' }}>
                                            {percent}% Used
                                        </span>
                                    )}
                                </div>

                                {/* Progress Bar Container */}
                                <div style={{ width: '100%', height: '8px', background: 'var(--bg-muted)', borderRadius: '999px', overflow: 'hidden' }}>
                                    <div
                                        style={{
                                            width: `${percent}%`,
                                            height: '100%',
                                            background: isExceeded ? 'var(--danger)' : percent > 80 ? 'var(--warning)' : 'var(--primary)',
                                            borderRadius: '999px',
                                            transition: 'width 0.4s ease'
                                        }}
                                    />
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}