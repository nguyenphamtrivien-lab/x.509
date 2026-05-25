import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { KeyRound } from 'lucide-react';
import api from '../api';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = new URLSearchParams();
      data.append('username', formData.username);
      data.append('password', formData.password);
      
      const response = await api.post('/auth/login', data, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('role', response.data.role);
      localStorage.setItem('username', formData.username);
      
      if (response.data.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/customer');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng nhập thất bại. Kiểm tra lại thông tin.');
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
      <div className="glass-panel" style={{ width: '400px', textAlign: 'center' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
          <div style={{ background: 'var(--primary)', padding: '15px', borderRadius: '50%' }}>
            <KeyRound size={32} color="white" />
          </div>
        </div>
        <h2 style={{ marginBottom: '20px' }}>Đăng Nhập PKI</h2>
        {error && <div style={{ color: 'var(--danger)', marginBottom: '15px', fontSize: '0.9rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', padding: '10px', borderRadius: '6px' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <input 
            className="input-field" 
            placeholder="Tên đăng nhập" 
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            required
          />
          <input 
            className="input-field" 
            type="password" 
            placeholder="Mật khẩu" 
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
          />
          <button type="submit" className="btn" style={{ width: '100%', marginTop: '10px', height: '45px' }}>
            Đăng Nhập
          </button>
        </form>
        <div style={{ marginTop: '20px', fontSize: '0.9rem', color: '#94a3b8' }}>
          Chưa có tài khoản? <Link to="/register" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 'bold' }}>Đăng ký ngay</Link>
        </div>
      </div>
    </div>
  );
};
export default Login;
