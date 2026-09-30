import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
    Search,
    Trash2,
    Edit3,
    SlidersHorizontal,
    ArrowUpDown,
    X,
    Check
} from 'lucide-react';
import api from '../services/api';
import './Expenses.css';

const CATEGORIES = ['All Categories', 'Food', 'Shopping', 'Transport', 'Bills', 'Entertainment', 'Health', 'Education', 'Travel', 'Groceries', 'Other'];

export default function Expenses() {
    const [expenses, setExpenses] = useState([]);
    const [loading, setLoading] = useState(true);

    // Search, Filter & Sort State
    const [search, setSearch] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('All Categories');
    const [sortKey, setSortKey] = useState('date-desc');

    // Pagination
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 8;

    // Edit Modal State
    const [editingItem, setEditingItem] = useState(null);

    const fetchExpenses = useCallback(async () => {
        try {
            setLoading(true);
            const res = await api.get('/expenses');
            setExpenses(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchExpenses();
    }, [fetchExpenses]);

    // Requirement: useMemo for filtering and sorting transactions
    const filteredExpenses = useMemo(() => {
        return expenses
            .filter((item) => {
                const matchesSearch = item.title.toLowerCase().includes(search.toLowerCase()) ||
                    (item.description && item.description.toLowerCase().includes(search.toLowerCase()));
                const matchesCategory = categoryFilter === 'All Categories' || item.category === categoryFilter;
                return matchesSearch && matchesCategory;
            })
            .sort((a, b) => {
                if (sortKey === 'amount-asc') return a.amount - b.amount;
                if (sortKey === 'amount-desc') return b.amount - a.amount;
                if (sortKey === 'date-asc') return new Date(a.date) - new Date(b.date);
                return new Date(b.date) - new Date(a.date);
            });
    }, [expenses, search, categoryFilter, sortKey]);

    // Paginated partition
    const paginatedExpenses = useMemo(() => {
        const start = (currentPage - 1) * itemsPerPage;
        return filteredExpenses.slice(start, start + itemsPerPage);
    }, [filteredExpenses, currentPage]);

    const totalPages = Math.ceil(filteredExpenses.length / itemsPerPage) || 1;

    // Requirement: useCallback for Delete
    const handleDelete = useCallback(async (id) => {
        if (!window.confirm('Are you sure you want to delete this transaction record?')) return;
        try {
            await api.delete(`/expenses/${id}`);
            setExpenses(prev => prev.filter(e => e.id !== id));
        } catch (err) {
            alert('Failed to delete expense.');
        }
    }, []);

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            const res = await api.put(`/expenses/${editingItem.id}`, {
                ...editingItem,
                amount: parseFloat(editingItem.amount)
            });
            setExpenses(prev => prev.map(item => item.id === editingItem.id ? res.data : item));
            setEditingItem(null);
        } catch {
            alert('Failed to update expense entry.');
        }
    };

    return (
        <div>
            <div style={{ marginBottom: '24px' }}>
                <h2 className="page-title">Ledger & Transactions</h2>
                <p className="page-desc">Comprehensive transaction records with multi-dimensional filtering.</p>
            </div>

            {/* Toolbar Controls */}
            <div className="toolbar-card">
                <div className="search-box">
                    <Search size={18} color="var(--text-muted)" />
                    <input
                        type="text"
                        placeholder="Search by description, vendor, or title..."
                        value={search}
                        onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
                        className="search-input"
                    />
                </div>

                <div className="filter-group">
                    <select
                        value={categoryFilter}
                        onChange={(e) => { setCategoryFilter(e.target.value); setCurrentPage(1); }}
                        className="filter-select"
                    >
                        {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>

                    <select
                        value={sortKey}
                        onChange={(e) => setSortKey(e.target.value)}
                        className="filter-select"
                    >
                        <option value="date-desc">Date: Newest First</option>
                        <option value="date-asc">Date: Oldest First</option>
                        <option value="amount-desc">Amount: Highest First</option>
                        <option value="amount-asc">Amount: Lowest First</option>
                    </select>
                </div>
            </div>

            {/* Transactions Data Table */}
            <div className="table-wrapper">
                <table className="expense-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Title</th>
                            <th>Category</th>
                            <th>Method</th>
                            <th>Amount</th>
                            <th style={{ textAlign: 'right' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan="6" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                                    Loading transactions...
                                </td>
                            </tr>
                        ) : paginatedExpenses.length === 0 ? (
                            <tr>
                                <td colSpan="6" style={{ textAlign: 'center', padding: '40px' }}>
                                    <p style={{ fontWeight: '600', color: 'var(--text-main)' }}>No matching transactions found</p>
                                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                                        Adjust your query or record a new transaction to begin.
                                    </p>
                                </td>
                            </tr>
                        ) : (
                            paginatedExpenses.map((item) => (
                                <tr key={item.id}>
                                    <td>{item.date}</td>
                                    <td>
                                        <strong>{item.title}</strong>
                                        {item.description && <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-subtle)' }}>{item.description}</span>}
                                    </td>
                                    <td><span className="category-tag">{item.category}</span></td>
                                    <td>{item.payment_method || 'UPI'}</td>
                                    <td><strong>₹{Number(item.amount).toLocaleString('en-IN')}</strong></td>
                                    <td style={{ textAlign: 'right' }}>
                                        <div className="action-btn-group" style={{ justifyContent: 'flex-end' }}>
                                            <button
                                                onClick={() => setEditingItem(item)}
                                                className="btn-icon-action"
                                                title="Edit Entry"
                                            >
                                                <Edit3 size={16} />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(item.id)}
                                                className="btn-icon-action delete"
                                                title="Delete Entry"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>

                {/* Pagination Bar */}
                <div className="pagination-bar">
                    <span>Showing {paginatedExpenses.length} of {filteredExpenses.length} entries</span>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                            disabled={currentPage <= 1}
                            onClick={() => setCurrentPage(p => p - 1)}
                            className="btn-page"
                        >
                            Previous
                        </button>
                        <span style={{ padding: '6px 10px', fontSize: '0.8125rem' }}>
                            Page {currentPage} of {totalPages}
                        </span>
                        <button
                            disabled={currentPage >= totalPages}
                            onClick={() => setCurrentPage(p => p + 1)}
                            className="btn-page"
                        >
                            Next
                        </button>
                    </div>
                </div>
            </div>

            {/* Edit Modal */}
            {editingItem && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
                            <h3 style={{ fontSize: '1.125rem', fontWeight: 700 }}>Edit Transaction</h3>
                            <button
                                onClick={() => setEditingItem(null)}
                                style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <form onSubmit={handleUpdate}>
                            <div className="form-group">
                                <label className="form-label">Title</label>
                                <input
                                    type="text"
                                    required
                                    value={editingItem.title}
                                    onChange={(e) => setEditingItem({ ...editingItem, title: e.target.value })}
                                    className="form-control"
                                />
                            </div>

                            <div className="form-grid-2">
                                <div className="form-group">
                                    <label className="form-label">Amount (₹)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        required
                                        value={editingItem.amount}
                                        onChange={(e) => setEditingItem({ ...editingItem, amount: e.target.value })}
                                        className="form-control"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Category</label>
                                    <select
                                        value={editingItem.category}
                                        onChange={(e) => setEditingItem({ ...editingItem, category: e.target.value })}
                                        className="form-control"
                                    >
                                        {CATEGORIES.filter(c => c !== 'All Categories').map(cat => (
                                            <option key={cat} value={cat}>{cat}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
                                <button
                                    type="button"
                                    onClick={() => setEditingItem(null)}
                                    className="btn-page"
                                >
                                    Cancel
                                </button>
                                <button type="submit" className="btn-submit" style={{ width: 'auto', padding: '8px 18px' }}>
                                    Save Updates
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}