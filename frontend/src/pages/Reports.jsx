import React, { useState, useEffect, useMemo } from 'react';
import { Download, Calendar, ArrowUpRight, TrendingDown } from 'lucide-react';
import api from '../services/api';

export default function Reports() {
    const [selectedMonth, setSelectedMonth] = useState('2026-03');
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

    const monthExpenses = useMemo(() => {
        return expenses.filter(e => e.date.startsWith(selectedMonth));
    }, [expenses, selectedMonth]);

    const totalSpent = useMemo(() => {
        return monthExpenses.reduce((sum, item) => sum + Number(item.amount), 0);
    }, [monthExpenses]);

    const biggestExpense = useMemo(() => {
        if (monthExpenses.length === 0) return null;
        return [...monthExpenses].sort((a, b) => b.amount - a.amount)[0];
    }, [monthExpenses]);

    const handlePrint = () => {
        window.print();
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h2 className="page-title">Financial Statements & Reports</h2>
                    <p className="page-desc">Comprehensive monthly audits and balance disclosures.</p>
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                    <select
                        value={selectedMonth}
                        onChange={(e) => setSelectedMonth(e.target.value)}
                        className="filter-select"
                    >
                        <option value="2026-01">January 2026</option>
                        <option value="2026-02">February 2026</option>
                        <option value="2026-03">March 2026</option>
                        <option value="2026-04">April 2026</option>
                    </select>

                    <button onClick={handlePrint} className="btn-page" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Download size={14} /> Export / Print
                    </button>
                </div>
            </div>

            <div className="form-card" style={{ maxWidth: '100%', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '14px' }}>
                    Statement Summary: {selectedMonth}
                </h3>

                <div className="metrics-grid">
                    <div className="kpi-card">
                        <div>
                            <span className="kpi-label">Month Total Spending</span>
                            <div className="kpi-value">₹{totalSpent.toLocaleString('en-IN')}</div>
                        </div>
                    </div>
                    <div className="kpi-card">
                        <div>
                            <span className="kpi-label">Highest Expense</span>
                            <div className="kpi-value" style={{ fontSize: '1.25rem' }}>
                                {biggestExpense ? `₹${Number(biggestExpense.amount).toLocaleString('en-IN')}` : 'None'}
                            </div>
                            <span className="kpi-subtext" style={{ color: 'var(--text-muted)' }}>
                                {biggestExpense?.title || 'No logged records'}
                            </span>
                        </div>
                    </div>
                </div>

                <div style={{ marginTop: '20px', padding: '16px', background: 'var(--bg-app)', borderRadius: 'var(--radius-sm)' }}>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: '4px' }}>AI Financial Review</h4>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                        {totalSpent > 40000
                            ? `Spending velocity in ${selectedMonth} was above standard conservative bands. Food and general merchandise represent the primary deviation.`
                            : `Disciplined burn rate maintained in ${selectedMonth}. Your savings rate remained healthy above targets.`}
                    </p>
                </div>
            </div>
        </div>
    );
}