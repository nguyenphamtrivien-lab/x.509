import React, { useState, useEffect } from 'react';

const MyCerts = () => {
  const [certs, setCerts] = useState([]);

  useEffect(() => {
    fetchCerts();
  }, []);

  const fetchCerts = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:8000/customer/certs', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCerts(Array.isArray(data) ? data : []); 
      }
    } catch (error) {
      console.error("Error fetching certs", error);
    }
  };

  const handleDownloadPEM = (cert) => {
    if (!cert.pem_data) {
      alert("Dữ liệu chứng chỉ trống!");
      return;
    }
    const blob = new Blob([cert.pem_data], { type: 'application/x-x509-ca-cert' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `cert_${cert.serial_number}.pem`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleRevoke = async (certId) => {
    if(!window.confirm("Bạn có chắc chắn muốn yêu cầu thu hồi chứng chỉ này? Hành động này không thể hoàn tác.")) return;
    
    const token = localStorage.getItem('token');
    const res = await fetch(`http://localhost:8000/customer/certs/${certId}/request-revoke`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (res.ok) {
      alert("Đã gửi yêu cầu thu hồi chứng chỉ!");
      fetchCerts();
    } else {
      const data = await res.json();
      alert("Lỗi: " + (data.detail || "Không thể yêu cầu thu hồi"));
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Chứng chỉ của tôi</h1>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="p-4 font-semibold text-gray-700">Serial Number</th>
              <th className="p-4 font-semibold text-gray-700">Tổ chức cấp (Issuer)</th>
              <th className="p-4 font-semibold text-gray-700">Hạn sử dụng</th>
              <th className="p-4 font-semibold text-gray-700">Trạng thái</th>
              <th className="p-4 font-semibold text-gray-700 text-center">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {certs.map(cert => (
              <tr key={cert.id} className="hover:bg-gray-50 transition-colors">
                <td className="p-4 font-mono text-sm">{cert.serial_number}</td>
                <td className="p-4">{cert.issuer}</td>
                <td className="p-4">{new Date(cert.valid_to).toLocaleDateString('vi-VN')}</td>
                <td className="p-4">
                  <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${cert.status === 'Active' ? 'bg-green-100 text-green-800' : 
                      cert.status === 'Revoked' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {cert.status}
                  </span>
                </td>
                <td className="p-4 flex space-x-2 justify-center">
                  <button onClick={() => handleDownloadPEM(cert)} disabled={!cert.pem_data}
                    className="bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50">
                    Tải PEM
                  </button>
                  <button onClick={() => handleRevoke(cert.id)} disabled={cert.status !== 'Active'}
                    className="border border-red-600 text-red-600 px-3 py-1.5 rounded text-sm hover:bg-red-50 disabled:opacity-50 disabled:border-gray-300 disabled:text-gray-400">
                    Thu hồi
                  </button>
                </td>
              </tr>
            ))}
            {certs.length === 0 && (
              <tr><td colSpan="5" className="p-8 text-center text-gray-500">Bạn chưa có chứng chỉ nào trong hệ thống.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MyCerts;