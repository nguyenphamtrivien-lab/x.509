import React, { useState } from 'react';
import { ShieldOff } from 'lucide-react';
import api from '../../api';

const CrlLookup = () => {
  const [crlData, setCrlData] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFetch = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/customer/crl', { responseType: 'text' });
      setCrlData(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Danh sách CRL chưa được tạo. Admin cần chạy "Cập nhật CRL" trước.');
      } else {
        setError(err.response?.data?.detail || 'Không thể tải danh sách CRL.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCrl = () => {
    const blob = new Blob([crlData], { type: 'application/x-pem-file' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'crl.pem');
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ShieldOff /> Tra Cứu Danh Sách Thu Hồi (CRL)
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '20px', lineHeight: '1.6' }}>
        Certificate Revocation List (CRL) chứa danh sách các chứng chỉ đã bị thu hồi bởi hệ thống CA. Bạn có thể tải file CRL này về để kiểm tra tính hợp lệ của chứng chỉ.
      </p>

      <button className="btn" onClick={handleFetch} disabled={loading} style={{ marginBottom: '20px' }}>
        {loading ? 'Đang tải...' : 'Tải Danh Sách CRL Từ Hệ Thống'}
      </button>

      {error && (
        <div style={{ color: '#f59e0b', marginBottom: '15px', fontSize: '0.9rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', padding: '12px', borderRadius: '6px', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
          ⚠️ {error}
        </div>
      )}

      {crlData && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h4 style={{ color: 'var(--success)' }}>Nội dung CRL (PEM Format)</h4>
            <button className="btn btn-success" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={handleDownloadCrl}>
              Tải file CRL.pem
            </button>
          </div>
          <textarea
            readOnly
            value={crlData}
            className="input-field"
            style={{ height: '300px', fontFamily: 'monospace', fontSize: '13px', resize: 'none', backgroundColor: 'rgba(16, 185, 129, 0.05)' }}
          />
        </div>
      )}
    </div>
  );
};
export default CrlLookup;
