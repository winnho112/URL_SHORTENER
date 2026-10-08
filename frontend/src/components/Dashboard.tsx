interface Props {
  onLogout: () => void;
}

export default function Dashboard({ onLogout }: Props) {
  function handleLogout() {
    localStorage.removeItem("access_token");
    onLogout();
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md text-center">
        <h1 className="mb-4 text-2xl font-bold text-gray-900">
          Welcome to your Dashboard
        </h1>
        <p className="mb-6 text-gray-600">
          You are logged in. Link management features are coming soon.
        </p>
        <button
          onClick={handleLogout}
          className="rounded bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700"
        >
          Log Out
        </button>
      </div>
    </div>
  );
}