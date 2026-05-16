# File: backend/auth_engine.py
from typing import Dict, Any

class AuthEngine:
    """
    AGENT_AUTH core logic.
    Handles Supabase Auth integration, RBAC, and Auth UI components.
    """
    
    def generate_auth_middleware(self) -> str:
        return """# File: middleware/auth.py
from fastapi import Request, HTTPException
from supabase import create_client

async def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Logic to verify Supabase JWT
    return {"id": "user_123", "role": "authenticated"}
"""

    def generate_login_ui(self, primary_color: str) -> str:
        return f"""// File: components/Login.jsx
'use client';
import {{ supabase }} from '../lib/supabase';

export const Login = () => {{
    const handleLogin = async (email, password) => {{
        const {{ data, error }} = await supabase.auth.signInWithPassword({{ email, password }});
    }};

    return (
        <div style={{{{ padding: '2rem', border: '1px solid {primary_color}33', borderRadius: '12px' }}}}>
            <h2 style={{{{ color: '{primary_color}' }}}}>Login</h2>
            <input type="email" placeholder="Email" style={{{{ width: '100%', margin: '0.5rem 0' }}}} />
            <input type="password" placeholder="Password" style={{{{ width: '100%', margin: '0.5rem 0' }}}} />
            <button style={{{{ background: '{primary_color}', color: '#000', width: '100%' }}}}>Sign In</button>
        </div>
    );
}};
"""

    def generate_rls_sql(self, table_name: str) -> str:
        return f"""-- File: auth/policies.sql
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own {table_name}" 
ON {table_name} FOR SELECT 
USING (auth.uid() = created_by);
"""

agent_auth = AuthEngine()
