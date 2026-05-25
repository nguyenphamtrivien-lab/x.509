import React, { useState, useEffect } from 'react';
import { ListChecks, CheckCircle, XCircle } from 'lucide-react';
import api from '../../api';

const Requests = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchRequests = async () => {
    try {
      const response = await api.get('/admin/csrs');
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

  const handleAction = async (id, action) => {
    let payload = {};
    
    if (action === 'approve') {
      const password = window.prompt(`Nhập mật khẩu Root CA để DUYỆT yêu cầu #${id} (Ký chứng chỉ):`);
      if (!password) return;
      payload = { password };
    } else {
      if (!window.confirm(`Bạn có chắc chắn TỪ CHỐI yêu cầu #${id}?`)) return;
    }

    try {
      const endpoint = action === 'approve' ? `/admin/approve-csr/${id}` : `/admin/reject-csr/${id}`;
      
      if (action === 'approve') {
        await api.post(endpoint, payload);
      } else {
        await api.post(endpoint);
      }
      
      alert(`Đã xử lý thành công!`);
      fetchRequests();
    } catch (err) {
      alert("Lỗi: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ListChecks /> Quản Lý Yêu Cầu Cấp Chứng Chỉ
      </h2>

      {loading ? (
        <p style={{ color: '#94a3b8' }}>Đang tải danh sách...</p>
      ) : requests.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
          <p style={{ color: '#94a3b8' }}>Chưa có yêu cầu nào.</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>User ID</th>
              <th>Trạng thái</th>
              <th>Ngày nộp</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {requests.map(req => (
              <tr key={req.id}>
                <td>{req.id}</td>
                <td>{req.user_id}</td>
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
                <td>{new Date(req.created_at).toLocaleString()}</td>
                <td style={{ display: 'flex', gap: '8px' }}>
                  {req.status === 'pending' && (
                    <>
                      <button className="btn btn-success" style={{ padding: '6px 10px', fontSize: '13px' }} onClick={() => handleAction(req.id, 'approve')}>
                        <CheckCircle size={14} /> Duyệt
                      </button>
                      <button className="btn btn-danger" style={{ padding: '6px 10px', fontSize: '13px' }} onClick={() => handleAction(req.id, 'reject')}>
                        <XCircle size={14} /> Từ chối
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
export default Requests;
