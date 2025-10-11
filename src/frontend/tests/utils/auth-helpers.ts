import { expect } from "../fixtures";

export async function getAuthToken(request: any) {
  const formData = new URLSearchParams();
  formData.append("username", "aiexec");
  formData.append("password", "aiexec");

  const loginResponse = await request.post("/api/v1/login", {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    data: formData.toString(),
  });

  expect(loginResponse.status()).toBe(200);
  const tokenData = await loginResponse.json();
  return tokenData.access_token;
}
