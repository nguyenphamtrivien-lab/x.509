import React, { useState, useEffect } from 'react';
import { ScrollText } from 'lucide-react';
import api from '../../api';

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await api.get('/admin/audit-logs');
        setLogs(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  const getActionColor = (action) => {
    if (action.includes('APPROVE')) return 'var(--success)';
    if (action.includes('REJECT') || action.includes('REVOKE')) return 'var(--danger)';
    if (action.includes('GEN_ROOT')) return '#f59e0b';
    if (action.includes('CRL')) return '#8b5cf6';
    return 'var(--primary)';
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <ScrollText /> Nhật Ký Hệ Thống (Audit Logs)
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '20px' }}>
        Theo dõi toàn bộ hoạt động chính của hệ thống PKI: Tạo Root CA, Duyệt/Từ chối CSR, Thu hồi chứng chỉ, Cập nhật CRL...
      </p>

      {loading ? (
        <p style={{ color: '#94a3b8' }}>Đang tải nhật ký...</p>
      ) : logs.length === 0 ? (
        <div style={{ padding: '30px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
          <p style={{ color: '#94a3b8' }}>Chưa có hoạt động nào được ghi nhận.</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Thời gian</th>
              <th>Hành động</th>
              <th>User ID</th>
              <th>Chi tiết</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td>{log.id}</td>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>
                  <span style={{
                    padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold',
                    backgroundColor: `${getActionColor(log.action)}20`,
                    color: getActionColor(log.action)
                  }}>
                    {log.action}
                  </span>
                </td>
                <td>{log.user_id || '—'}</td>
                <td style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{log.details || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
export default AuditLogs;
