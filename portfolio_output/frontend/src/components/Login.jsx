// File: components/Login.jsx
'use client';
import { supabase } from '../lib/supabase';

export const Login = () => {
    const handleLogin = async (email, password) => {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    };

    return (
        <div style={{ padding: '2rem', border: '1px solid #00f3ff33', borderRadius: '12px' }}>
            <h2 style={{ color: '#00f3ff' }}>Login</h2>
            <input type="email" placeholder="Email" style={{ width: '100%', margin: '0.5rem 0' }} />
            <input type="password" placeholder="Password" style={{ width: '100%', margin: '0.5rem 0' }} />
            <button style={{ background: '#00f3ff', color: '#000', width: '100%' }}>Sign In</button>
        </div>
    );
};
