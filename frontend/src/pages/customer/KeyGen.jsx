import React, { useState } from 'react';
import { Key } from 'lucide-react';
import api from '../../api';

const KeyGen = () => {
  const [password, setPassword] = useState('');
  const [keys, setKeys] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenKey = async () => {
    if (!password) {
      alert("Vui lòng nhập mật khẩu bảo vệ khóa!");
      return;
    }
    setLoading(true);
    try {
      const response = await api.post('/customer/gen-keypair', { password });
      setKeys(response.data);
    } catch (err) {
      alert("Lỗi tạo khóa: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Đã copy vào bộ nhớ đệm!');
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Key /> Khởi Tạo Cặp Khóa RSA
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '20px', lineHeight: '1.6' }}>
        Hệ thống sẽ tự động sinh ra một cặp khóa (Public/Private Key). <br/>
        <b>Private Key</b> của bạn sẽ được mã hóa bằng thuật toán <b>AES-256</b> dựa trên mật khẩu bạn cung cấp bên dưới để đảm bảo an toàn tuyệt đối. Đừng quên mật khẩu này!
      </p>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px', maxWidth: '500px' }}>
        <input 
          className="input-field" 
          type="password" 
          placeholder="Mật khẩu bảo vệ Private Key..." 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ marginBottom: 0 }}
        />
        <button className="btn" onClick={handleGenKey} disabled={loading} style={{ whiteSpace: 'nowrap' }}>
          {loading ? 'Đang xử lý...' : 'Tạo Cặp Khóa Mới'}
        </button>
      </div>

      {keys && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h4 style={{ color: 'var(--success)' }}>Public Key (Dùng tạo CSR)</h4>
              <button className="btn" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => copyToClipboard(keys.public_key)}>Copy</button>
            </div>
            <textarea 
              readOnly 
              value={keys.public_key} 
              className="input-field" 
              style={{ height: '350px', fontSize: '13px', fontFamily: 'monospace', resize: 'none', backgroundColor: 'rgba(16, 185, 129, 0.05)' }} 
            />
          </div>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h4 style={{ color: 'var(--danger)' }}>Encrypted Private Key</h4>
              <button className="btn" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => copyToClipboard(keys.private_key)}>Copy</button>
            </div>
            <textarea 
              readOnly 
              value={keys.private_key} 
              className="input-field" 
              style={{ height: '350px', fontSize: '13px', fontFamily: 'monospace', resize: 'none', borderColor: 'rgba(239, 68, 68, 0.3)', backgroundColor: 'rgba(239, 68, 68, 0.05)' }} 
            />
          </div>
        </div>
      )}
    </div>
  );
};
export default KeyGen;
