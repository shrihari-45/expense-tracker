import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    Receipt,
    PlusCircle,
    PiggyBank,
    PieChart,
    Bot,
    FileSpreadsheet,
    LogOut,
    Menu,
    X,
    Sparkles
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import './AppLayout.css';

const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Transactions', path: '/expenses', icon: Receipt },
    { name: 'Add Expense', path: '/add-expense', icon: PlusCircle },
    { name: 'Budgets', path: '/budgets', icon: PiggyBank },
    { name: 'Analytics', path: '/analytics', icon: PieChart },
    { name: 'AI Assistant', path: '/assistant', icon: Bot },
    { name: 'Reports', path: '/reports', icon: FileSpreadsheet },
];

export default function AppLayout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="app-container">
            {/* Desktop Sidebar */}
            <aside className="sidebar">
                <div className="brand-section">
                    <div className="brand-icon">
                        <Sparkles size={18} />
                    </div>
                    <div>
                        <h1 className="brand-title">SpendWise AI</h1>
                        <p className="brand-subtitle">Fintech Hub</p>
                    </div>
                </div>

                <nav className="nav-menu">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            end={item.path === '/'}
                            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                        >
                            <item.icon size={18} />
                            {item.name}
                        </NavLink>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <div className="user-badge">
                        <p className="user-name">{user?.name || 'Authorized Member'}</p>
                        <p className="user-email">{user?.email || 'session@spendwise.ai'}</p>
                    </div>
                    <button onClick={handleLogout} className="btn-signout">
                        <LogOut size={16} />
                        Sign Out
                    </button>
                </div>
            </aside>

            {/* Main Viewport */}
            <div className="content-viewport">
                <header className="mobile-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div className="brand-icon" style={{ width: '32px', height: '32px' }}>
                            <Sparkles size={16} />
                        </div>
                        <span style={{ fontWeight: '700' }}>SpendWise AI</span>
                    </div>
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        style={{ border: 'none', background: 'transparent', cursor: 'pointer' }}
                    >
                        {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </header>

                <main className="main-scroll-area">
                    <div className="container-inner">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
}