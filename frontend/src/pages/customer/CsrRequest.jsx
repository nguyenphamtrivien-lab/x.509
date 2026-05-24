/*
File: frontend/src/pages/customer/CsrRequest.jsx
Description: Page to submit a Certificate Signing Request (CSR).
TODO:
- Add form for subject details (CN, O, OU, Country, etc.).
- Allow uploading a CSR file or pasting PEM data.
- Call backend API to submit the CSR.
*/

import React from 'react';

import React, { useState } from 'react';

const CsrRequest = () => {
  const [formData, setFormData] = useState({
    commonName: '',
    organization: '',
    organizationalUnit: '',
    country: '',
    csrData: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Submitting CSR:", formData);
    alert("Đã gửi yêu cầu CSR thành công!");
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Nộp Yêu cầu Chứng chỉ (CSR)</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium">Common Name (CN)</label>
            <input type="text" name="commonName" onChange={handleChange} className="w-full border p-2 rounded" placeholder="example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium">Organization (O)</label>
            <input type="text" name="organization" onChange={handleChange} className="w-full border p-2 rounded" />
          </div>
          <div>
            <label className="block text-sm font-medium">Organizational Unit (OU)</label>
            <input type="text" name="organizationalUnit" onChange={handleChange} className="w-full border p-2 rounded" />
          </div>
          <div>
            <label className="block text-sm font-medium">Country (C)</label>
            <input type="text" name="country" onChange={handleChange} className="w-full border p-2 rounded" maxLength="2" placeholder="VN" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium">Hoặc dán nội dung CSR (PEM format)</label>
          <textarea name="csrData" onChange={handleChange} className="w-full border p-2 rounded h-32" placeholder="-----BEGIN CERTIFICATE REQUEST-----..."></textarea>
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Gửi Yêu Cầu</button>
      </form>
    </div>
  );
};

export default CsrRequest;
