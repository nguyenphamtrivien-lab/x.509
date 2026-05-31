import React, { useState, useEffect } from 'react';
import { ShieldCheck, Download, AlertTriangle, Clock } from 'lucide-react';
import api from '../../api';

const MyCerts = () => {
  const [certs, setCerts] = useState([]);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [certsRes, reqsRes] = await Promise.all([
        api.get('/customer/certs'),
        api.get('/customer/csr-requests')
      ]);
      setCerts(certsRes.data);
      setRequests(reqsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
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
      fetchData();
    } catch (err) {
      alert("Lỗi: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      {/* PHẦN 1: DANH SÁCH CHỨNG CHỈ ĐÃ CẤP */}
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ShieldCheck /> Chứng Chỉ Của Tôi
      </h2>

      {loading ? (
        <p style={{ color: '#94a3b8' }}>Đang tải dữ liệu...</p>
      ) : certs.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', marginBottom: '40px' }}>
          <p style={{ color: '#94a3b8' }}>Bạn chưa có chứng chỉ nào được cấp phát.</p>
        </div>
      ) : (
        <table style={{ marginBottom: '40px' }}>
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
                <td>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn" style={{ padding: '6px 10px', fontSize: '13px' }} onClick={() => handleDownload(cert.id, cert.serial_number)}>
                      <Download size={14} /> Tải
                    </button>
                    {cert.status === 'active' && (
                      <button className="btn btn-danger" style={{ padding: '6px 10px', fontSize: '13px' }} onClick={() => handleRequestRevoke(cert.id)}>
                        <AlertTriangle size={14} /> Thu hồi
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* PHẦN 2: DANH SÁCH YÊU CẦU CSR VÀ TRẠNG THÁI */}
      <h2 style={{ marginBottom: '20px', marginTop: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Clock /> Danh Sách Yêu Cầu Cấp Phát (CSR)
      </h2>

      {loading ? (
        <p style={{ color: '#94a3b8' }}>Đang tải dữ liệu...</p>
      ) : requests.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
          <p style={{ color: '#94a3b8' }}>Chưa có yêu cầu cấp phát CSR nào được gửi.</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Ngày gửi</th>
              <th>Mã CSR (Xem trước)</th>
              <th>Trạng thái yêu cầu</th>
            </tr>
          </thead>
          <tbody>
            {requests.map(req => (
              <tr key={req.id}>
                <td>{req.id}</td>
                <td>{new Date(req.created_at).toLocaleString()}</td>
                <td style={{ fontFamily: 'monospace', fontSize: '12px', color: '#94a3b8' }}>
                  {req.csr_data.substring(0, 50)}...
                </td>
                <td>
                  <span style={{ 
                    padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold',
                    backgroundColor: req.status === 'approved' ? 'rgba(16, 185, 129, 0.2)' : 
                                   req.status === 'rejected' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                    color: req.status === 'approved' ? 'var(--success)' : 
                           req.status === 'rejected' ? 'var(--danger)' : 'var(--primary)'
                  }}>
                    {req.status.toUpperCase()}
                  </span>
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
