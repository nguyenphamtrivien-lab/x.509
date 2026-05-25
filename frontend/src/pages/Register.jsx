import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus } from 'lucide-react';
import api from '../api';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: '', password: '', role: 'customer' });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/auth/register', formData);
      alert('Đăng ký thành công! Vui lòng đăng nhập.');
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng ký thất bại. Tên đăng nhập có thể đã tồn tại.');
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
      <div className="glass-panel" style={{ width: '400px', textAlign: 'center' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
          <div style={{ background: 'var(--success)', padding: '15px', borderRadius: '50%' }}>
            <UserPlus size={32} color="white" />
          </div>
        </div>
        <h2 style={{ marginBottom: '20px' }}>Đăng Ký Tài Khoản</h2>
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
          <select 
            className="input-field"
            value={formData.role}
            onChange={(e) => setFormData({...formData, role: e.target.value})}
            style={{ color: 'white', backgroundColor: 'rgba(15, 23, 42, 0.9)' }}
          >
            <option value="customer">Khách hàng (Customer)</option>
            <option value="admin">Quản trị viên (Admin)</option>
          </select>
          <button type="submit" className="btn btn-success" style={{ width: '100%', marginTop: '10px', height: '45px' }}>
            Đăng Ký
          </button>
        </form>
        <div style={{ marginTop: '20px', fontSize: '0.9rem', color: '#94a3b8' }}>
          Đã có tài khoản? <Link to="/login" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 'bold' }}>Đăng nhập ngay</Link>
        </div>
      </div>
    </div>
  );
};
export default Register;
