// File: src/components/ui/GlassInput.tsx
import React from 'react';

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const GlassInput: React.FC<GlassInputProps> = ({ label, className = '', ...props }) => {
  return (
    <div className="input-group" style={{ marginBottom: '1rem' }}>
      {label && <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>{label}</label>}
      <input className={`glass-input ${className}`} {...props} />
    </div>
  );
};
