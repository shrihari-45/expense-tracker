import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '../services/api';
import './AddExpense.css';

const CATEGORIES = [
    'Food', 'Shopping', 'Transport', 'Bills',
    'Entertainment', 'Health', 'Education', 'Travel', 'Groceries', 'Other'
];

const PAYMENT_METHODS = ['Cash', 'UPI', 'Credit Card', 'Debit Card', 'Bank Transfer'];

export default function AddExpense() {
    const [formData, setFormData] = useState({
        title: '',
        amount: '',
        category: 'Food',
        date: new Date().toISOString().split('T')[0],
        payment_method: 'UPI',
        description: '',
    });

    const [aiSuggested, setAiSuggested] = useState(null);
    const [status, setStatus] = useState({ type: '', message: '' });
    const [loading, setLoading] = useState(false);

    // Requirement: useRef automatically focusing title input on mount
    const titleInputRef = useRef(null);

    useEffect(() => {
        titleInputRef.current?.focus();
    }, []);

    // Predictive Auto-Categorization on debounce
    useEffect(() => {
        const handler = setTimeout(async () => {
            if (formData.title.trim().length > 3) {
                try {
                    const res = await api.post('/ai/categorize', { text: formData.title });
                    if (res.data?.category && CATEGORIES.includes(res.data.category)) {
                        setAiSuggested(res.data.category);
                    }
                } catch {
                    // Rule-based fallback if offline
                    const text = formData.title.toLowerCase();
                    if (text.includes('uber') || text.includes('metro') || text.includes('fuel')) setAiSuggested('Transport');
                    else if (text.includes('domino') || text.includes('dinner') || text.includes('lunch')) setAiSuggested('Food');
                    else if (text.includes('amazon') || text.includes('shoes') || text.includes('nike')) setAiSuggested('Shopping');
                }
            }
        }, 500);

        return () => clearTimeout(handler);
    }, [formData.title]);

    const acceptAiSuggestion = () => {
        if (aiSuggested) {
            setFormData(prev => ({ ...prev, category: aiSuggested }));
            setAiSuggested(null);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.amount || Number(formData.amount) <= 0) {
            setStatus({ type: 'error', message: 'Amount must be greater than zero.' });
            return;
        }

        setLoading(true);
        setStatus({ type: '', message: '' });

        try {
            await api.post('/expenses', {
                ...formData,
                amount: parseFloat(formData.amount)
            });
            setStatus({ type: 'success', message: 'Transaction recorded successfully.' });
            setFormData({
                title: '',
                amount: '',
                category: 'Food',
                date: new Date().toISOString().split('T')[0],
                payment_method: 'UPI',
                description: '',
            });
            setAiSuggested(null);
            titleInputRef.current?.focus();
        } catch (err) {
            setStatus({
                type: 'error',
                message: err.response?.data?.message || 'Failed to submit transaction.'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <h2 className="page-title">Add Expense</h2>
                <p className="page-desc">Record outlays with real-time category inference.</p>
            </div>

            <div className="form-card">
                {status.message && (
                    <div className={`alert-box ${status.type === 'success' ? 'alert-success' : 'alert-error'}`}>
                        {status.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                        {status.message}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Expense Title *</label>
                        <input
                            ref={titleInputRef}
                            type="text"
                            required
                            placeholder="e.g., Domino's Pizza or Uber to office"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            className="form-control"
                        />
                    </div>

                    {aiSuggested && (
                        <div className="ai-recommendation-bar">
                            <span className="ai-recommendation-text">
                                <Sparkles size={16} />
                                Suggested: <strong>{aiSuggested}</strong>
                            </span>
                            <button
                                type="button"
                                onClick={acceptAiSuggestion}
                                className="btn-apply-suggestion"
                            >
                                Apply
                            </button>
                        </div>
                    )}

                    <div className="form-grid-2">
                        <div className="form-group">
                            <label className="form-label">Amount (₹) *</label>
                            <input
                                type="number"
                                step="0.01"
                                required
                                placeholder="0.00"
                                value={formData.amount}
                                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                                className="form-control"
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Category</label>
                            <select
                                value={formData.category}
                                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                className="form-control"
                            >
                                {CATEGORIES.map(cat => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="form-grid-2">
                        <div className="form-group">
                            <label className="form-label">Date</label>
                            <input
                                type="date"
                                required
                                value={formData.date}
                                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                                className="form-control"
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Payment Method</label>
                            <select
                                value={formData.payment_method}
                                onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                                className="form-control"
                            >
                                {PAYMENT_METHODS.map(method => (
                                    <option key={method} value={method}>{method}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Description / Memo</label>
                        <textarea
                            rows="3"
                            placeholder="Optional notes..."
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            className="form-control"
                        />
                    </div>

                    <button type="submit" disabled={loading} className="btn-submit">
                        {loading ? 'Recording...' : 'Save Expense'}
                        <ArrowRight size={16} />
                    </button>
                </form>
            </div>
        </div>
    );
}