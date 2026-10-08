import { useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL;

interface Props {
  onLogin: () => void;
}

export default function AuthForm({ onLogin }: Props) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Friendly error messages for common Supabase errors
  function friendlyError(msg: string): string {
    if (msg.toLowerCase().includes("invalid login")) return "Invalid email or password.";
    if (msg.toLowerCase().includes("already registered")) return "This email is already registered.";
    if (msg.toLowerCase().includes("password")) return "Password must be at least 6 characters.";
    if (msg.toLowerCase().includes("email")) return "Please enter a valid email address.";
    return msg || "Something went wrong. Please try again.";
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/signup";
      const body =
        mode === "login"
          ? { email, password }
          : { email, password, full_name: fullName };

      const res = await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(friendlyError(data.detail || ""));
        return;
      }

      // Login returns tokens; signup returns a user object
      if (mode === "login" && data.access_token) {
        localStorage.setItem("access_token", data.access_token);
        onLogin();
      } else if (mode === "signup") {
        // After signup, switch to login so the user can log in
        setMode("login");
        setError("");
        alert("Account created! Please log in.");
      }
    } catch {
      setError("Cannot reach the server. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">
          URL Shortener
        </h1>

        {/* Toggle between login and signup */}
        <div className="mb-6 flex justify-center gap-4">
          <button
            type="button"
            onClick={() => { setMode("login"); setError(""); }}
            className={`px-4 py-2 font-medium rounded ${
              mode === "login" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"
            }`}
          >
            Log In
          </button>
          <button
            type="button"
            onClick={() => { setMode("signup"); setError(""); }}
            className={`px-4 py-2 font-medium rounded ${
              mode === "signup" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"
            }`}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "signup" && (
            <input
              type="text"
              placeholder="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="w-full rounded border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="w-full rounded border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />

          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Please wait…" : mode === "login" ? "Log In" : "Sign Up"}
          </button>
        </form>
      </div>
    </div>
  );
}