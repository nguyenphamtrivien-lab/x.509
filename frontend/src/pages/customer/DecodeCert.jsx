import React, { useState } from 'react';
import { FileSearch } from 'lucide-react';
import api from '../../api';

const DecodeCert = () => {
  const [certPem, setCertPem] = useState('');
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDecode = async () => {
    if (!certPem.includes('BEGIN CERTIFICATE')) {
      setError('Vui lòng nhập nội dung chứng chỉ PEM hợp lệ!');
      return;
    }
    setLoading(true);
    setError('');
    setInfo(null);
    try {
      const response = await api.post('/customer/certs/decode', { cert_pem: certPem });
      setInfo(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể giải mã chứng chỉ.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <FileSearch /> Giải Mã Chứng Chỉ (Decode)
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '20px', lineHeight: '1.6' }}>
        Dán nội dung file <b>.crt / .pem</b> của bất kỳ chứng chỉ nào vào ô bên dưới. Hệ thống sẽ phân tích và hiển thị toàn bộ thông tin kỹ thuật.
      </p>

      <textarea
        className="input-field"
        style={{ height: '200px', fontFamily: 'monospace', resize: 'vertical' }}
        placeholder={"-----BEGIN CERTIFICATE-----\nMIIDxTCCAq2gAw...\n-----END CERTIFICATE-----"}
        value={certPem}
        onChange={(e) => setCertPem(e.target.value)}
      />

      {error && (
        <div style={{ color: 'var(--danger)', marginBottom: '15px', fontSize: '0.9rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', padding: '10px', borderRadius: '6px' }}>{error}</div>
      )}

      <button className="btn" onClick={handleDecode} disabled={loading || !certPem} style={{ marginBottom: '20px' }}>
        {loading ? 'Đang phân tích...' : 'Giải Mã Chứng Chỉ'}
      </button>

      {info && (
        <div style={{ marginTop: '10px' }}>
          <h3 style={{ color: 'var(--success)', marginBottom: '15px' }}>📋 Thông tin Chứng chỉ</h3>
          <table>
            <tbody>
              <tr><td style={{ fontWeight: 'bold', color: '#94a3b8', width: '200px' }}>Serial Number</td><td style={{ fontFamily: 'monospace' }}>{info.serial_number}</td></tr>
              <tr><td style={{ fontWeight: 'bold', color: '#94a3b8' }}>Subject</td><td>{info.subject}</td></tr>
              <tr><td style={{ fontWeight: 'bold', color: '#94a3b8' }}>Issuer</td><td>{info.issuer}</td></tr>
              <tr><td style={{ fontWeight: 'bold', color: '#94a3b8' }}>Valid From</td><td>{new Date(info.valid_from).toLocaleString()}</td></tr>
              <tr><td style={{ fontWeight: 'bold', color: '#94a3b8' }}>Valid To</td><td>{new Date(info.valid_to).toLocaleString()}</td></tr>
              <tr><td style={{ fontWeight: 'bold', color: '#94a3b8' }}>Signature Algorithm</td><td>{info.signature_algorithm}</td></tr>
              <tr><td style={{ fontWeight: 'bold', color: '#94a3b8' }}>Public Key Size</td><td>{info.public_key_size} bits</td></tr>
            </tbody>
          </table>

          {info.extensions && info.extensions.length > 0 && (
            <>
              <h4 style={{ color: '#94a3b8', marginTop: '20px', marginBottom: '10px' }}>Extensions (X.509v3)</h4>
              <table>
                <thead>
                  <tr>
                    <th>Tên</th>
                    <th>OID</th>
                    <th>Critical</th>
                    <th>Giá trị</th>
                  </tr>
                </thead>
                <tbody>
                  {info.extensions.map((ext, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 'bold' }}>{ext.name}</td>
                      <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{ext.oid}</td>
                      <td>
                        <span style={{
                          padding: '2px 6px', borderRadius: '4px', fontSize: '11px',
                          backgroundColor: ext.critical ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                          color: ext.critical ? 'var(--danger)' : 'var(--primary)'
                        }}>
                          {ext.critical ? 'YES' : 'NO'}
                        </span>
                      </td>
                      <td style={{ fontSize: '12px', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>{ext.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}
    </div>
  );
};
export default DecodeCert;
