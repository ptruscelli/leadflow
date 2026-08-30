import StaffNavbar from "../components/StaffNavbar";
export default function LeadsLayout({ children }) {
  return (
    <>
      <StaffNavbar />
      {children}
    </>
  );
}