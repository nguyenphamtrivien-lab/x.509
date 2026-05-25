import React, { useState } from 'react';
import { FileSignature } from 'lucide-react';
import api from '../../api';
import { useNavigate } from 'react-router-dom';

const CsrRequest = () => {
  const [csrPem, setCsrPem] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!csrPem.includes('BEGIN CERTIFICATE REQUEST')) {
      alert('Vui lòng nhập định dạng CSR hợp lệ!');
      return;
    }
    setLoading(true);
    try {
      await api.post('/customer/submit-csr', { csr_pem: csrPem });
      alert('Đã nộp yêu cầu CSR thành công! Vui lòng chờ Admin phê duyệt.');
      navigate('/customer/certs');
    } catch (err) {
      alert("Lỗi nộp CSR: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <FileSignature /> Gửi Yêu Cầu Chứng Chỉ (CSR)
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '20px', lineHeight: '1.6' }}>
        Dán mã <b>Certificate Signing Request (CSR)</b> của bạn vào bên dưới. CSR thường được tạo ra từ Public Key và chứa thông tin tên miền Website của bạn.
      </p>

      <textarea 
        className="input-field" 
        style={{ height: '350px', fontFamily: 'monospace', resize: 'vertical' }}
        placeholder="-----BEGIN CERTIFICATE REQUEST-----&#10;MIICXzCCAUcCAQAwGjEYMBY...&#10;-----END CERTIFICATE REQUEST-----"
        value={csrPem}
        onChange={(e) => setCsrPem(e.target.value)}
      />

      <button className="btn btn-success" onClick={handleSubmit} disabled={loading || !csrPem}>
        {loading ? 'Đang gửi...' : 'Nộp Yêu Cầu Duyệt'}
      </button>
    </div>
  );
};
export default CsrRequest;
