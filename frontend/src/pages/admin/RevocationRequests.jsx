import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle } from 'lucide-react';
import api from '../../api';

const RevocationRequests = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchRequests = async () => {
    try {
      const response = await api.get('/admin/revoke-requests');
      setRequests(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleRevoke = async (id, serialNumber) => {
    if (!window.confirm(`Bạn có chắc chắn phê duyệt thu hồi chứng chỉ Serial: ${serialNumber}?`)) return;
    try {
      await api.post(`/admin/revoke-cert/${id}`);
      alert(`Đã thu hồi chứng chỉ thành công!`);
      fetchRequests();
    } catch (err) {
      alert("Lỗi: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ShieldAlert /> Yêu Cầu Thu Hồi Chứng Chỉ
      </h2>

      {loading ? (
        <p style={{ color: '#94a3b8' }}>Đang tải danh sách...</p>
      ) : requests.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
          <p style={{ color: '#94a3b8' }}>Chưa có yêu cầu thu hồi nào cần xử lý.</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Serial Number</th>
              <th>Subject</th>
              <th>Trạng thái</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {requests.map(req => (
              <tr key={req.id}>
                <td>{req.id}</td>
                <td style={{ fontFamily: 'monospace', color: '#cbd5e1' }}>{req.serial_number}</td>
                <td>{req.subject}</td>
                <td>
                  <span style={{ 
                    padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold',
                    backgroundColor: 'rgba(245, 158, 11, 0.2)',
                    color: '#f59e0b'
                  }}>
                    {req.status.toUpperCase()}
                  </span>
                </td>
                <td>
                  <button className="btn btn-danger" style={{ padding: '6px 10px', fontSize: '13px' }} onClick={() => handleRevoke(req.id, req.serial_number)}>
                    <CheckCircle size={14} /> Phê duyệt Thu hồi
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default RevocationRequests;
