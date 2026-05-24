import React, { useState, useEffect } from 'react';

const Account = () => {
  const [userInfo, setUserInfo] = useState({ username: 'customer_user', role: 'customer' });
  const [passwordData, setPasswordData] = useState({ oldPassword: '', newPassword: '' });
  const [message, setMessage] = useState('');

  useEffect(() => {
    console.log("Fetching user profile...");
  }, []);

  const handleChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    console.log("Đổi mật khẩu với dữ liệu:", passwordData);
    setMessage('Yêu cầu đổi mật khẩu đã được gửi!');
    setPasswordData({ oldPassword: '', newPassword: '' });
  };
  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded shadow mt-8">
      <h1 className="text-2xl font-bold border-b pb-2 mb-6">Quản Lý Tài Khoản</h1>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Thông tin cá nhân</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Tên đăng nhập</p>
            <p className="font-medium text-lg">{userInfo.username}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Vai trò hệ thống</p>
            <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-semibold">
              {userInfo.role.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Đổi mật khẩu</h2>
        {message && <div className="bg-green-100 text-green-700 p-2 rounded mb-4">{message}</div>}
        
        <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700">Mật khẩu hiện tại</label>
            <input 
              type="password" name="oldPassword" 
              value={passwordData.oldPassword}
              onChange={handleChange} 
              className="mt-1 w-full border p-2 rounded" 
              required 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Mật khẩu mới</label>
            <input 
              type="password" name="newPassword" 
              value={passwordData.newPassword}
              onChange={handleChange} 
              className="mt-1 w-full border p-2 rounded" 
              required 
            />
          </div>
          <button type="submit" className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-900">
            Cập Nhật Mật Khẩu
          </button>
        </form>
      </div>
    </div>
  );
};

export default Account;