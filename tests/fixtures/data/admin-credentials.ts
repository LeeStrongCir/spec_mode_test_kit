/**
 * 管理员初始凭据测试数据
 * 对应 T004: 准备测试数据集
 */

export const adminCredentials = {
  username: 'admin',
  password: 'admin@123',
};

export const adminLoginSuccess = {
  status: 200,
  body: {
    token: 'mock-jwt-token-for-admin',
    userId: 'admin-001',
    role: 'admin',
    firstLogin: true, // 首次登录，需要修改密码
  },
};
