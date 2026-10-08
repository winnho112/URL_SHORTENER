import { useState } from "react";
import AuthForm from "./components/AuthForm";
import Dashboard from "./components/Dashboard";

function App() {
  // Check if user is already logged in
  const [loggedIn, setLoggedIn] = useState(
    () => !!localStorage.getItem("access_token")
  );

  if (!loggedIn) {
    return <AuthForm onLogin={() => setLoggedIn(true)} />;
  }

  return <Dashboard onLogout={() => setLoggedIn(false)} />;
}

export default App;