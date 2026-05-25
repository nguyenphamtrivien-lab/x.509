import React, { useState } from 'react';
import { Lock } from 'lucide-react';
import api from '../../api';

const ChangePassword = () => {
  const [formData, setFormData] = useState({ old_password: '', new_password: '', confirm_password: '' });
  const [message, setMessage] = useState({ text: '', type: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ text: '', type: '' });

    if (formData.new_password !== formData.confirm_password) {
      setMessage({ text: 'Mật khẩu mới và xác nhận không khớp!', type: 'error' });
      return;
    }
    if (formData.new_password.length < 3) {
      setMessage({ text: 'Mật khẩu mới phải có ít nhất 3 ký tự!', type: 'error' });
      return;
    }

    try {
      await api.post('/auth/change-password', {
        old_password: formData.old_password,
        new_password: formData.new_password
      });
      setMessage({ text: 'Đổi mật khẩu thành công!', type: 'success' });
      setFormData({ old_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setMessage({ text: err.response?.data?.detail || 'Đổi mật khẩu thất bại.', type: 'error' });
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Lock /> Đổi Mật Khẩu
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '20px' }}>
        Nhập mật khẩu cũ và mật khẩu mới để thay đổi.
      </p>

      {message.text && (
        <div style={{
          padding: '12px', borderRadius: '6px', marginBottom: '15px', fontSize: '0.9rem',
          backgroundColor: message.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          color: message.type === 'success' ? 'var(--success)' : 'var(--danger)',
          border: `1px solid ${message.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
        }}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ maxWidth: '400px' }}>
        <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '5px', display: 'block' }}>Mật khẩu hiện tại</label>
        <input
          className="input-field"
          type="password"
          placeholder="Nhập mật khẩu cũ..."
          value={formData.old_password}
          onChange={(e) => setFormData({ ...formData, old_password: e.target.value })}
          required
        />
        <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '5px', display: 'block' }}>Mật khẩu mới</label>
        <input
          className="input-field"
          type="password"
          placeholder="Nhập mật khẩu mới..."
          value={formData.new_password}
          onChange={(e) => setFormData({ ...formData, new_password: e.target.value })}
          required
        />
        <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '5px', display: 'block' }}>Xác nhận mật khẩu mới</label>
        <input
          className="input-field"
          type="password"
          placeholder="Nhập lại mật khẩu mới..."
          value={formData.confirm_password}
          onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
          required
        />
        <button type="submit" className="btn" style={{ width: '100%', marginTop: '10px' }}>
          Xác Nhận Đổi Mật Khẩu
        </button>
      </form>
    </div>
  );
};
export default ChangePassword;
