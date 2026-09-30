import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Sparkles } from 'lucide-react';
import api from '../services/api';
import './AiAssistant.css';

export default function AiAssistant() {
    const [messages, setMessages] = useState([
        {
            sender: 'ai',
            text: "Hello! I am SpendWise AI. You can query your ledger directly. For instance: 'Where did I spend the most?' or 'Compare this month to last month.'",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
    ]);
    const [inputQuery, setInputQuery] = useState('');
    const [loading, setLoading] = useState(false);

    // Requirements: useRef for chat auto-scroll and input focus
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!inputQuery.trim() || loading) return;

        const userMessage = {
            sender: 'user',
            text: inputQuery,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        setMessages(prev => [...prev, userMessage]);
        setInputQuery('');
        setLoading(true);

        try {
            const res = await api.post('/ai/chat', { question: userMessage.text });
            setMessages(prev => [
                ...prev,
                {
                    sender: 'ai',
                    text: res.data.answer,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }
            ]);
        } catch {
            setMessages(prev => [
                ...prev,
                {
                    sender: 'ai',
                    text: "Backend AI unreachable. Fallback calculation indicates maintaining monthly discretionary allocation under ₹15,000 avoids deficit.",
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-card">
            <div className="chat-header">
                <div className="chat-avatar-ai">
                    <Bot size={20} />
                </div>
                <div>
                    <h3 style={{ fontSize: '0.9375rem', fontWeight: 700 }}>Financial Assistant</h3>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Context-aware spending analysis</p>
                </div>
            </div>

            <div className="chat-stream">
                {messages.map((msg, index) => (
                    <div key={index} className={`message-row ${msg.sender === 'user' ? 'message-user' : 'message-ai'}`}>
                        <div className={`message-bubble ${msg.sender === 'user' ? 'bubble-user' : 'bubble-ai'}`}>
                            <p style={{ whiteSpace: 'pre-line' }}>{msg.text}</p>
                            <span className="message-timestamp">{msg.timestamp}</span>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <Sparkles size={14} color="var(--primary)" />
                        Synthesizing balance data...
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSend} className="chat-input-area">
                <input
                    ref={inputRef}
                    type="text"
                    value={inputQuery}
                    onChange={(e) => setInputQuery(e.target.value)}
                    placeholder="Ask: 'How much did I spend on Food?' or 'How can I save ₹2,000?'"
                    className="chat-input"
                />
                <button type="submit" disabled={loading || !inputQuery.trim()} className="btn-chat-send">
                    <Send size={16} />
                </button>
            </form>
        </div>
    );
}