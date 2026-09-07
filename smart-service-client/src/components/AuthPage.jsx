import React, { useState } from "react";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";
import LogoImage from "./LogoImage";

// Top-level auth screen that switches between the login and register forms
export default function AuthPage({ onLoginSuccess, onRegisterSuccess }) {
  const [mode, setMode] = useState("login");

  return (
    <main
      className={`auth-shell ${
        mode === "register" ? "register-mode" : "login-mode"
      }`}
      dir="ltr"
    >
      <header className="auth-brand-header">
        <LogoImage small />
      </header>

      <section className="auth-center">
        <div className="auth-welcome">
          <h1>{mode === "login" ? "Sign in" : "Create account"}</h1>

          <p>
            A smart customer service platform for conversations, subscriptions,
            and company knowledge databases.
          </p>
        </div>

        {mode === "login" ? (
          <LoginForm
            onLoginSuccess={onLoginSuccess}
            onMoveToRegister={() => setMode("register")}
          />
        ) : (
          <RegisterForm
            onRegisterSuccess={onRegisterSuccess}
            onMoveToLogin={() => setMode("login")}
          />
        )}
      </section>
    </main>
  );
}