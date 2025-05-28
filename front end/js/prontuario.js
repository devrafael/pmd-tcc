document.addEventListener("DOMContentLoaded", function () {
  const header = document.querySelector("header h1");
  header.innerHTML = "";
  const h1 = document.createElement("h1");
  h1.innerHTML = `BUSQUE UM PRONTURÁRIO NO CAMPO ACIMA ⬆️`;

  header.appendChild(h1);
});

function atualizarHeader(nome, prontuario) {
  const header = document.querySelector("header h1");
  header.textContent = `Paciente: ${nome} (${prontuario})`;
}

function cardTemplate(titulo, conteudo) {
  const section = document.createElement("section");
  section.className = "card";

  const h2 = document.createElement("h2");
  h2.textContent = titulo;

  const article = document.createElement("article");
  const ul = document.createElement("ul");

  const itens = conteudo
    .split(";")
    .map((item) => item.trim())
    .filter((item) => item);

  itens.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item + ";";
    ul.appendChild(li);
  });

  article.appendChild(ul);
  section.appendChild(h2);
  section.appendChild(article);

  return section;
}

function atualizarMain(data) {
  const main = document.querySelector("main.cards-container");
  main.innerHTML = "";

  main.appendChild(cardTemplate("Queixas Principais", data.queixas_principais));
  main.appendChild(cardTemplate("Medicamentos Continuos", data.medicamentos_continuos));
  main.appendChild(cardTemplate("Prescrição Médica", data.prescicao_medica));
  main.appendChild(cardTemplate("Exames", data.exames));
}

async function buscarProntuario() {
  const numero_prontuario = document.getElementById("input-prontuario").value;
  const token = localStorage.getItem("token");

  try {
    const response = await fetch(
      `http://localhost:8000/prontuario/?prontuario=${numero_prontuario}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Erro na requisição: " + response.status);
    }

    const data = await response.json();
    atualizarHeader(data.paciente, data.numero_prontuario);
    atualizarMain(data);
  } catch (error) {
    console.error("Erro ao buscar prontuário:", error);
  }
}
