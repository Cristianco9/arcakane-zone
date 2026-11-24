// Rutas de autenticación. Si prefieres, mueve estas líneas a src/app/routes.ts.
export const authPaths = {
  resetPassword: "/restablecer/:uid/:token",
  login: "/iniciar-sesion",
  forgotPassword: "/recuperar-contrasena",
} as const;
