import React, { useState } from 'react';
import { ShieldAlert, RefreshCw } from 'lucide-react';
import api from '../../api';

const DashboardOverview = () => {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [crlLoading, setCrlLoading] = useState(false);

  const handleGenRootCA = async () => {
    if (!password) {
      alert("Cần mật khẩu bảo vệ Root CA!");
      return;
    }
    if (!window.confirm("CẢNH BÁO: Việc tạo mới Root CA sẽ làm vô hiệu hóa các chứng chỉ cũ. Tiếp tục?")) return;
    
    setLoading(true);
    try {
      await api.post('/admin/gen-root-ca', { password });
      alert("Đã tạo Root CA thành công!");
    } catch (err) {
      alert("Lỗi tạo Root CA: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateCRL = async () => {
    const pwd = window.prompt("Nhập mật khẩu Root CA để ký danh sách CRL:");
    if (!pwd) return;
    setCrlLoading(true);
    try {
      await api.post('/admin/update-crl', { password: pwd });
      alert("Đã cập nhật danh sách CRL mới nhất!");
    } catch (err) {
      alert("Lỗi cập nhật CRL: " + (err.response?.data?.detail || err.message));
    } finally {
      setCrlLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ShieldAlert color="var(--danger)" /> Quản Trị Hệ Thống PKI
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '30px', lineHeight: '1.6' }}>
        Chào mừng bạn đến với bảng điều khiển Admin. 
        Để hệ thống có thể cấp phát chứng chỉ, bạn cần phải khởi tạo <b>Root CA (Chứng chỉ gốc)</b>.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ border: '1px solid rgba(239, 68, 68, 0.3)', padding: '20px', borderRadius: '8px', backgroundColor: 'rgba(239, 68, 68, 0.05)' }}>
          <h3 style={{ color: 'var(--danger)', marginBottom: '15px' }}>Khởi tạo Root CA</h3>
          <p style={{ fontSize: '0.9rem', marginBottom: '15px', color: '#94a3b8' }}>
            Nhập mật khẩu an toàn để mã hóa khóa riêng tư của Root CA.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input 
              className="input-field" 
              type="password" 
              placeholder="Mật khẩu Root CA..." 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ marginBottom: 0 }}
            />
            <button className="btn btn-danger" onClick={handleGenRootCA} disabled={loading}>
              {loading ? 'Đang xử lý...' : 'Tạo Khóa Root CA'}
            </button>
          </div>
        </div>

        <div style={{ border: '1px solid rgba(245, 158, 11, 0.3)', padding: '20px', borderRadius: '8px', backgroundColor: 'rgba(245, 158, 11, 0.05)' }}>
          <h3 style={{ color: '#f59e0b', marginBottom: '15px' }}>Cập Nhật Danh Sách CRL</h3>
          <p style={{ fontSize: '0.9rem', marginBottom: '15px', color: '#94a3b8' }}>
            Gom các chứng chỉ đã bị thu hồi vào danh sách Certificate Revocation List (CRL) và dùng Root CA để ký.
          </p>
          <button className="btn" style={{ backgroundColor: '#f59e0b', width: '100%', marginTop: '38px' }} onClick={handleUpdateCRL} disabled={crlLoading}>
            <RefreshCw size={18} /> {crlLoading ? 'Đang cập nhật...' : 'Chạy Update CRL'}
          </button>
        </div>
      </div>
    </div>
  );
};
export default DashboardOverview;
