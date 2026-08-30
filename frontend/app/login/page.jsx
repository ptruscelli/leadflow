import LoginForm from "../components/LoginForm";
import PublicNavbar from "../components/PublicNavbar";

export default function LoginPage() {
  return (
    <>
      <PublicNavbar />
      <div className="px-4 py-10">
        <LoginForm />
      </div>
    </>
  );
}