import React, { useState } from 'react';

const CsrRequest = () => {
  const [csrData, setCsrData] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch('http://localhost:8000/customer/submit-csr', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ csr_data: csrData }) // Key theo schema cơ sở dữ liệu
      });

      const data = await response.json();
      if (response.ok) {
        alert("Nộp CSR thành công. Đang chờ Admin duyệt!");
        setCsrData('');
      } else {
        alert("Lỗi: " + (data.detail || "Không thể nộp CSR"));
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Nộp Yêu Cầu Chứng Chỉ (CSR)</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-2 font-medium">Nội dung CSR (định dạng PEM):</label>
          <textarea 
            value={csrData}
            onChange={(e) => setCsrData(e.target.value)}
            className="w-full h-64 border border-gray-300 p-3 rounded font-mono text-sm"
            placeholder="-----BEGIN CERTIFICATE REQUEST-----&#10;...&#10;-----END CERTIFICATE REQUEST-----"
            required
          />
        </div>
        <button type="submit" className="bg-green-600 text-white px-6 py-2 rounded font-medium hover:bg-green-700">
          Gửi CSR
        </button>
      </form>
    </div>
  );
};

export default CsrRequest;