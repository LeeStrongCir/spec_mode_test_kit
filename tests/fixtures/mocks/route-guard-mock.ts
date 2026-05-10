
export const mockRouteGuard = {
  isAuthenticated: false,

  login() {
    this.isAuthenticated = true;
  },

  logout() {
    this.isAuthenticated = false;
  },

  protectedRoute(targetPath: string) {
    if (!this.isAuthenticated) {
      return { redirected: true, destination: '/login?redirect=' + targetPath };
    }
    return { redirected: false, destination: targetPath };
  },

  publicRoute(targetPath: string) {
    return { redirected: false, destination: targetPath };
  },
};
