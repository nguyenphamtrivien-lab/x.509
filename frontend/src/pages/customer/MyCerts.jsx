import React, { useState, useEffect } from 'react';
import { ShieldCheck, Download, AlertTriangle } from 'lucide-react';
import api from '../../api';

const MyCerts = () => {
  const [certs, setCerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchCerts = async () => {
    try {
      const response = await api.get('/customer/certs');
      setCerts(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCerts();
  }, []);

  const handleDownload = async (certId, serialHex) => {
    try {
      const response = await api.get(`/customer/certs/${certId}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificate_${serialHex}.crt`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Lỗi tải file");
    }
  };

  const handleRequestRevoke = async (certId) => {
    if (!window.confirm("Bạn có chắc chắn muốn yêu cầu thu hồi chứng chỉ này? Hành động này không thể hoàn tác.")) return;
    try {
      await api.post(`/customer/certs/${certId}/request-revoke`);
      alert("Đã gửi yêu cầu thu hồi!");
      fetchCerts();
    } catch (err) {
      alert("Lỗi: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ShieldCheck /> Chứng Chỉ Của Tôi
      </h2>

      {loading ? (
        <p style={{ color: '#94a3b8' }}>Đang tải dữ liệu...</p>
      ) : certs.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
          <p style={{ color: '#94a3b8' }}>Bạn chưa có chứng chỉ nào.</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Serial Number</th>
              <th>Subject</th>
              <th>Status</th>
              <th>Valid Until</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {certs.map(cert => (
              <tr key={cert.id}>
                <td>{cert.id}</td>
                <td style={{ fontFamily: 'monospace', color: '#cbd5e1' }}>{cert.serial_number.substring(0, 12)}...</td>
                <td>{cert.subject}</td>
                <td>
                  <span style={{ 
                    padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold', letterSpacing: '0.05em',
                    backgroundColor: cert.status === 'active' ? 'rgba(16, 185, 129, 0.2)' : 
                                   cert.status === 'revoked' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: cert.status === 'active' ? 'var(--success)' : 
                           cert.status === 'revoked' ? 'var(--danger)' : '#f59e0b'
                  }}>
                    {cert.status.toUpperCase()}
                  </span>
                </td>
                <td>{new Date(cert.valid_to).toLocaleDateString()}</td>
                <td style={{ display: 'flex', gap: '8px' }}>
                  {cert.status === 'active' && (
                    <>
                      <button className="btn" style={{ padding: '6px 10px', fontSize: '13px' }} onClick={() => handleDownload(cert.id, cert.serial_number)}>
                        <Download size={14} /> Tải
                      </button>
                      <button className="btn btn-danger" style={{ padding: '6px 10px', fontSize: '13px' }} onClick={() => handleRequestRevoke(cert.id)}>
                        <AlertTriangle size={14} /> Thu hồi
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
export default MyCerts;
