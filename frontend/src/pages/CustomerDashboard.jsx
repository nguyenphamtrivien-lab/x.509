import React from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { KeyRound, FileSignature, ShieldCheck, ShieldOff, FileSearch, Lock, LogOut } from 'lucide-react';
import KeyGen from './customer/KeyGen';
import CsrRequest from './customer/CsrRequest';
import MyCerts from './customer/MyCerts';
import DecodeCert from './customer/DecodeCert';
import CrlLookup from './customer/CrlLookup';
import ChangePassword from './shared/ChangePassword';

const CustomerDashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const navItems = [
    { path: '/customer/keygen', label: 'Sinh Khóa (Keypair)', icon: KeyRound },
    { path: '/customer/csr', label: 'Xin Cấp Chứng Chỉ', icon: FileSignature },
    { path: '/customer/certs', label: 'Chứng Chỉ Của Tôi', icon: ShieldCheck },
    { path: '/customer/decode', label: 'Giải Mã Chứng Chỉ', icon: FileSearch },
    { path: '/customer/crl', label: 'Tra Cứu CRL', icon: ShieldOff },
    { path: '/customer/change-password', label: 'Đổi Mật Khẩu', icon: Lock },
  ];

  return (
    <div>
      <div className="header-bar">
        <h2>Xin chào, <span style={{ color: 'var(--primary)' }}>{localStorage.getItem('username')}</span></h2>
        <button className="btn btn-danger" onClick={handleLogout}>
          <LogOut size={18} /> Đăng Xuất
        </button>
      </div>
      
      <div style={{ display: 'flex', gap: '20px' }}>
        <div className="glass-panel" style={{ width: '250px', height: 'fit-content' }}>
          <h3 style={{ marginBottom: '15px', color: '#94a3b8', fontSize: '0.9rem' }}>MENU KHÁCH HÀNG</h3>
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
            <Route path="keygen" element={<KeyGen />} />
            <Route path="csr" element={<CsrRequest />} />
            <Route path="certs" element={<MyCerts />} />
            <Route path="decode" element={<DecodeCert />} />
            <Route path="crl" element={<CrlLookup />} />
            <Route path="change-password" element={<ChangePassword />} />
            <Route path="*" element={<KeyGen />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};
export default CustomerDashboard;
