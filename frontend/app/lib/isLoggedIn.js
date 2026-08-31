export async function isLoggedIn() {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/leads?page=1&page_size=1`,
      { credentials: "include" }
    );
    return response.ok;
  } catch {
    return false;
  }
}
