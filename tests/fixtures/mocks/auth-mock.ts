
const SUCCESS_TOKEN = 'mock-jwt-token';
const FAIL_MESSAGE = '用户名或密码错误';
const EMPTY_MESSAGE = '请输入用户名/密码';

export const mockAuthResponses = {
  success(credentials: { username: string; password: string }) {
    if (credentials.username === '' || credentials.password === '') {
      return { status: 400, body: { error: EMPTY_MESSAGE } };
    }
    if (credentials.username === 'admin' && credentials.password === 'admin@123') {
      return {
        status: 200,
        body: {
          token: SUCCESS_TOKEN,
          userId: 'admin-001',
          role: 'admin',
          firstLogin: true,
        },
      };
    }
    return { status: 401, body: { error: FAIL_MESSAGE } };
  },

  unauthorized() {
    return { status: 403, body: { error: '未授权访问' } };
  },

  expiredToken() {
    return { status: 401, body: { error: 'Token 已过期' } };
  },
};
