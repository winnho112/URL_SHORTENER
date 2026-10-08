import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL;

interface Link {
  id: string;
  original_url: string;
  short_code: string;
  short_url: string;
  click_count: number;
  created_at: string;
}

interface Props {
  onLogout: () => void;
}

export default function Dashboard({ onLogout }: Props) {
  const [url, setUrl] = useState("");
  const [links, setLinks] = useState<Link[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const token = localStorage.getItem("access_token");

  // Helper: fetch with auth header, handle 401
  async function authFetch(path: string, options: RequestInit = {}) {
    const res = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...(options.headers || {}),
      },
    });
    if (res.status === 401) {
      localStorage.removeItem("access_token");
      onLogout();
      return null;
    }
    return res;
  }

  // Fetch the user's links on mount
  async function loadLinks() {
    const res = await authFetch("/links");
    if (!res) return;
    const data = await res.json();
    setLinks(data.links || []);
  }

  useEffect(() => {
    loadLinks();
  }, []);

  // Create a new short link
  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const trimmed = url.trim();
    if (!trimmed.startsWith("http://") && !trimmed.startsWith("https://")) {
      setError("URL must start with http:// or https://");
      return;
    }
    setLoading(true);
    try {
      const res = await authFetch("/links", {
        method: "POST",
        body: JSON.stringify({ original_url: trimmed }),
      });
      if (!res) return;
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Failed to create link");
        return;
      }
      setLinks((prev) => [data, ...prev]);
      setUrl("");
    } catch {
      setError("Cannot reach the server. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  // Copy short_url to clipboard
  async function handleCopy(link: Link) {
    try {
      await navigator.clipboard.writeText(link.short_url);
      setCopiedId(link.id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      alert(link.short_url);
    }
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    onLogout();
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="flex items-center justify-between bg-white px-6 py-4 shadow-sm">
        <h1 className="text-xl font-bold text-gray-900">URL Shortener</h1>
        <button
          onClick={handleLogout}
          className="rounded bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
        >
          Log Out
        </button>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        {/* Create link form */}
        <form onSubmit={handleCreate} className="mb-8">
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Paste a URL to shorten
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="https://example.com/very/long/url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 rounded border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "…" : "Shorten"}
            </button>
          </div>
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        </form>

        {/* Links section header */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Your Links</h2>
          <button
            onClick={loadLinks}
            className="rounded bg-gray-200 px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-300"
          >
            Refresh
          </button>
        </div>

        {/* Links table */}
        {links.length === 0 ? (
          <p className="text-gray-500">No links yet. Create one above!</p>
        ) : (
          <div className="overflow-x-auto rounded-lg bg-white shadow">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
                <tr>
                  <th className="px-4 py-3">Original URL</th>
                  <th className="px-4 py-3">Short URL</th>
                  <th className="px-4 py-3 text-center">Clicks</th>
                  <th className="px-4 py-3">Created</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {links.map((link) => (
                  <tr key={link.id} className="border-b last:border-0">
                    <td className="max-w-xs truncate px-4 py-3 text-gray-800">
                      {link.original_url}
                    </td>
                    <td className="px-4 py-3 text-blue-600">
                      {link.short_url}
                    </td>
                    <td className="px-4 py-3 text-center text-gray-800">
                      {link.click_count}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {formatDate(link.created_at)}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleCopy(link)}
                        className="rounded bg-gray-200 px-2 py-1 text-xs font-medium text-gray-700 hover:bg-gray-300"
                      >
                        {copiedId === link.id ? "Copied!" : "Copy"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}