import React, { useState } from 'react';

const KeyGen = () => {
  const [formData, setFormData] = useState({
    key_type: 'RSA',
    key_size_or_curve: '2048',
    password: ''
  });
  const [keys, setKeys] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'key_type') {
      setFormData({
        ...formData,
        key_type: value,
        key_size_or_curve: value === 'RSA' ? '2048' : 'secp256r1'
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/customer/gen-keypair', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      if (response.ok) {
        setKeys(data);
        alert("Đã sinh khóa thành công! Vui lòng lưu trữ cẩn thận.");
      } else {
        alert("Lỗi: " + data.detail);
      }
    } catch (error) {
      console.error("Error generating keys:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6 border-b pb-2">Tạo Cặp Khóa (Keypair)</h1>
      <form onSubmit={handleGenerate} className="space-y-4 bg-white p-6 rounded shadow-sm border">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Loại Thuật Toán</label>
            <select name="key_type" value={formData.key_type} onChange={handleChange} className="w-full border p-2 rounded">
              <option value="RSA">RSA</option>
              <option value="EC">Elliptic Curve (EC)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Kích thước / Curve</label>
            <select name="key_size_or_curve" value={formData.key_size_or_curve} onChange={handleChange} className="w-full border p-2 rounded">
              {formData.key_type === 'RSA' ? (
                <>
                  <option value="2048">2048-bit</option>
                  <option value="4096">4096-bit</option>
                </>
              ) : (
                <>
                  <option value="secp256r1">secp256r1</option>
                  <option value="secp384r1">secp384r1</option>
                </>
              )}
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Mật khẩu bảo vệ Private Key <span className="text-red-500">*</span></label>
          <input 
            type="password" name="password" required 
            value={formData.password} onChange={handleChange} 
            className="w-full border p-2 rounded" 
            placeholder="Nhập mật khẩu để mã hóa khóa riêng tư..." 
          />
          <p className="text-xs text-gray-500 mt-1">Mật khẩu này dùng để bảo vệ Private Key bằng mã hóa. Hãy ghi nhớ nó!</p>
        </div>
        <button type="submit" disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Đang xử lý...' : 'Sinh Cặp Khóa'}
        </button>
      </form>

      {keys && (
        <div className="mt-8 space-y-4">
          <div>
            <h3 className="font-bold text-red-600 flex justify-between">
              <span>Encrypted Private Key</span>
            </h3>
            <textarea readOnly value={keys.encrypted_private_key} className="w-full h-40 border p-2 text-xs font-mono bg-gray-100 rounded focus:outline-none" />
          </div>
          <div>
            <h3 className="font-bold text-green-600">Public Key</h3>
            <textarea readOnly value={keys.public_key} className="w-full h-40 border p-2 text-xs font-mono bg-gray-100 rounded focus:outline-none" />
          </div>
        </div>
      )}
    </div>
  );
};

export default KeyGen;