/*
File: frontend/src/pages/customer/MyCerts.jsx
Description: Page to view customer's own certificates.
TODO:
- Fetch user's certificates from backend.
- Display certificate status (Active, Expired, Revoked).
- Provide download links for certificates.
- Provide button to request revocation.
*/

import React, { useState, useEffect } from 'react';

const MyCerts = () => {
  const [certs, setCerts] = useState([
    { id: 1, serial: "1A2B3C", subject: "CN=example.com", status: "Active", validTo: "2027-01-01" }
  ]);

  const handleDownload = (certId) => {
    console.log(`Downloading cert ${certId}...`);
  };

  const handleRevoke = (certId) => {
    if(window.confirm("Bạn có chắc chắn muốn thu hồi chứng chỉ này?")) {
      console.log(`Requested revocation for cert ${certId}`);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Chứng chỉ của tôi</h1>
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b">
            <th className="p-2">Serial</th>
            <th className="p-2">Subject</th>
            <th className="p-2">Hết hạn</th>
            <th className="p-2">Trạng thái</th>
            <th className="p-2">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          {certs.map(cert => (
            <tr key={cert.id} className="border-b">
              <td className="p-2">{cert.serial}</td>
              <td className="p-2">{cert.subject}</td>
              <td className="p-2">{cert.validTo}</td>
              <td className="p-2">
                <span className={`px-2 py-1 text-sm rounded ${cert.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {cert.status}
                </span>
              </td>
              <td className="p-2 space-x-2">
                <button onClick={() => handleDownload(cert.id)} className="bg-green-500 text-white px-3 py-1 rounded text-sm">Tải PEM</button>
                <button onClick={() => handleRevoke(cert.id)} className="bg-red-500 text-white px-3 py-1 rounded text-sm">Thu hồi</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MyCerts;
