document.querySelector("form").addEventListener("submit", function (event) {
  event.preventDefault();
  Login();
});

async function Login() {
  const username = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch("http://localhost:8000/api/token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password,
      }),
    });

    if (!response.ok) {
      throw new Error("Erro na requisição: " + response.status);
    }

    const data = await response.json();
    localStorage.setItem("token", data.access);
    localStorage.setItem("refresh", data.refresh);

    window.location.href = "pages/prontuario.html";
  } catch (error) {
    console.error("Erro ao fazer login:", error);
  }
}
