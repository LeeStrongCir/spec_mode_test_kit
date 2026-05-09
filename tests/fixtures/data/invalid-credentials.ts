/**
 * 无效/错误凭据测试数据
 * 对应 T004: 准备测试数据集 (SC-04, SC-05)
 */

// SC-04: 无效凭据
export const invalidCredentials = {
  wrongPassword: { username: 'admin', password: 'wrongpass' },
  wrongUsername: { username: 'wronguser', password: 'admin@123' },
  bothWrong: { username: 'wronguser', password: 'wrongpass' },
};

// SC-05: 空凭据
export const emptyCredentials = {
  emptyUsername: { username: '', password: 'admin@123' },
  emptyPassword: { username: 'admin', password: '' },
  bothEmpty: { username: '', password: '' },
};

// Mock 响应
export const authFailureResponse = {
  status: 401,
  body: { error: '用户名或密码错误' },
};

export const emptyInputResponse = {
  status: 400,
  body: { error: '请输入用户名/密码' },
};
