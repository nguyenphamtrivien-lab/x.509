import React from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { ShieldAlert, ListChecks, ShieldOff, ScrollText, Lock, LogOut } from 'lucide-react';
import DashboardOverview from './admin/DashboardOverview';
import Requests from './admin/Requests';
import RevocationRequests from './admin/RevocationRequests';
import AuditLogs from './admin/AuditLogs';
import ChangePassword from './shared/ChangePassword';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const navItems = [
    { path: '/admin/overview', label: 'Tổng Quan & Root CA', icon: ShieldAlert },
    { path: '/admin/requests', label: 'Duyệt Yêu Cầu', icon: ListChecks },
    { path: '/admin/revocations', label: 'Yêu Cầu Thu Hồi', icon: ShieldOff },
    { path: '/admin/audit-logs', label: 'Nhật Ký Hệ Thống', icon: ScrollText },
    { path: '/admin/change-password', label: 'Đổi Mật Khẩu', icon: Lock },
  ];

  return (
    <div>
      <div className="header-bar">
        <h2>Administrator: <span style={{ color: 'var(--danger)' }}>{localStorage.getItem('username')}</span></h2>
        <button className="btn btn-danger" onClick={handleLogout}>
          <LogOut size={18} /> Đăng Xuất
        </button>
      </div>
      
      <div style={{ display: 'flex', gap: '20px' }}>
        <div className="glass-panel" style={{ width: '250px', height: 'fit-content' }}>
          <h3 style={{ marginBottom: '15px', color: '#94a3b8', fontSize: '0.9rem' }}>MENU QUẢN TRỊ</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.includes(item.path);
              return (
                <Link 
                  key={item.path} 
                  to={item.path}
                  className="btn"
                  style={{ 
                    background: isActive ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                    justifyContent: 'flex-start'
                  }}
                >
                  <Icon size={18} /> {item.label}
                </Link>
              );
            })}
          </div>
        </div>
        
        <div className="glass-panel" style={{ flex: 1, minHeight: '60vh' }}>
          <Routes>
            <Route path="overview" element={<DashboardOverview />} />
            <Route path="requests" element={<Requests />} />
            <Route path="revocations" element={<RevocationRequests />} />
            <Route path="audit-logs" element={<AuditLogs />} />
            <Route path="change-password" element={<ChangePassword />} />
            <Route path="*" element={<DashboardOverview />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};
export default AdminDashboard;
