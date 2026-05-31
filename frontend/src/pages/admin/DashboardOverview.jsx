import React, { useState, useEffect } from 'react';
import { ShieldAlert, RefreshCw } from 'lucide-react';
import api from '../../api';

const DashboardOverview = () => {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [crlLoading, setCrlLoading] = useState(false);

  // State cho cấu hình thông số kỹ thuật chuẩn
  const [configs, setConfigs] = useState({
    asymmetric_algo: 'RSA',
    hash_algo: 'SHA256',
    validity_days: '365',
    root_key_size: '4096',
    client_key_size: '2048'
  });
  const [configLoading, setConfigLoading] = useState(true);
  const [saveLoading, setSaveLoading] = useState(false);

  const fetchConfigs = async () => {
    try {
      const response = await api.get('/admin/config');
      const configMap = {};
      response.data.forEach(item => {
        configMap[item.config_key] = item.config_value;
      });
      setConfigs(prev => ({
        ...prev,
        ...configMap
      }));
    } catch (err) {
      console.error("Lỗi tải cấu hình:", err);
    } finally {
      setConfigLoading(false);
    }
  };

  useEffect(() => {
    fetchConfigs();
  }, []);

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

  const handleSaveConfigs = async () => {
    setSaveLoading(true);
    try {
      const promises = Object.entries(configs).map(([key, val]) => 
        api.put('/admin/config', { key, value: String(val) })
      );
      await Promise.all(promises);
      alert("Đã lưu các thông số cấu hình hệ thống thành công!");
    } catch (err) {
      alert("Lỗi lưu cấu hình: " + (err.response?.data?.detail || err.message));
    } finally {
      setSaveLoading(false);
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

        <div style={{ 
          gridColumn: '1 / span 2', 
          border: '1px solid var(--border-color)', 
          padding: '25px', 
          borderRadius: '12px', 
          backgroundColor: 'rgba(255, 255, 255, 0.02)',
          marginTop: '10px'
        }}>
          <h3 style={{ color: 'var(--primary)', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            ⚙️ Cấu Hình Thông Số Kỹ Thuật Chuẩn
          </h3>
          <p style={{ fontSize: '0.9rem', marginBottom: '20px', color: '#94a3b8' }}>
            Thiết lập các thuật toán, độ dài khóa và hiệu lực cho việc sinh chứng nhận Root CA và ký số chứng chỉ khách hàng (CSR).
          </p>

          {configLoading ? (
            <p style={{ color: '#94a3b8' }}>Đang tải thông số cấu hình...</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div>
                <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '5px', display: 'block' }}>Thuật toán Bất đối xứng</label>
                <select 
                  className="input-field"
                  value={configs.asymmetric_algo}
                  onChange={(e) => setConfigs({ ...configs, asymmetric_algo: e.target.value })}
                  style={{ color: 'white', backgroundColor: 'rgba(15, 23, 42, 0.9)' }}
                >
                  <option value="RSA">RSA (Rivest-Shamir-Adleman)</option>
                  <option value="ECC" disabled>ECC (Elliptic Curve Cryptography - Sắp hỗ trợ)</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '5px', display: 'block' }}>Hàm băm mật mã (Hash Function)</label>
                <select 
                  className="input-field"
                  value={configs.hash_algo}
                  onChange={(e) => setConfigs({ ...configs, hash_algo: e.target.value })}
                  style={{ color: 'white', backgroundColor: 'rgba(15, 23, 42, 0.9)' }}
                >
                  <option value="SHA256">SHA-256 (Khuyên dùng)</option>
                  <option value="SHA384">SHA-384</option>
                  <option value="SHA512">SHA-512</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '5px', display: 'block' }}>Độ dài khóa Root CA (Bits)</label>
                <select 
                  className="input-field"
                  value={configs.root_key_size}
                  onChange={(e) => setConfigs({ ...configs, root_key_size: e.target.value })}
                  style={{ color: 'white', backgroundColor: 'rgba(15, 23, 42, 0.9)' }}
                >
                  <option value="2048">2048 bits</option>
                  <option value="3072">3072 bits</option>
                  <option value="4096">4096 bits (An toàn cao)</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '5px', display: 'block' }}>Độ dài khóa Khách hàng (Bits)</label>
                <select 
                  className="input-field"
                  value={configs.client_key_size}
                  onChange={(e) => setConfigs({ ...configs, client_key_size: e.target.value })}
                  style={{ color: 'white', backgroundColor: 'rgba(15, 23, 42, 0.9)' }}
                >
                  <option value="2048">2048 bits (Tiêu chuẩn)</option>
                  <option value="3072">3072 bits</option>
                  <option value="4096">4096 bits</option>
                </select>
              </div>

              <div style={{ gridColumn: '1 / span 2' }}>
                <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '5px', display: 'block' }}>Thời gian hiệu lực mặc định (Ngày)</label>
                <input 
                  className="input-field"
                  type="number"
                  placeholder="365"
                  value={configs.validity_days}
                  onChange={(e) => setConfigs({ ...configs, validity_days: e.target.value })}
                  min="1"
                />
              </div>

              <div style={{ gridColumn: '1 / span 2', display: 'flex', justifyContent: 'flex-end' }}>
                <button className="btn" onClick={handleSaveConfigs} disabled={saveLoading} style={{ minWidth: '150px' }}>
                  {saveLoading ? 'Đang lưu...' : 'Lưu Cấu Hình'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;
