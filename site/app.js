const board = document.getElementById("board");
const details = document.getElementById("details");
const tpl = document.getElementById("card-template");
const tagFilters = document.getElementById("tag-filters");
const countryFilters = document.getElementById("country-filters");

const TAG_LABELS = {
  "amplitude-analysis": "amplitude",
  "lattice-qcd": "lattice",
  "dyson-schwinger": "dyson-schwinger",
  "effective-field-theory": "eft",
  "heavy-hadrons": "heavy",
  "light-hadrons": "light",
  "exotics": "exotics",
  "qcd-sum-rules": "sum-rules",
  "experiment": "experiment",
  "machine-learning": "ml"
};

const TAG_COLOR = {
  "amplitude-analysis": "#e9f3fa",
  "lattice-qcd": "#ecf4e0",
  "dyson-schwinger": "#f2e8f7",
  "effective-field-theory": "#e8f0fd",
  "heavy-hadrons": "#fde9df",
  "light-hadrons": "#f4edd7",
  "exotics": "#fde6ef",
  "qcd-sum-rules": "#ebe8d9",
  "experiment": "#e2f3ef",
  "machine-learning": "#e7f0f9"
};

let members = [];
let activeTag = "";
let activeCountry = "";
let selectedId = "";
let query = "";
const search = document.getElementById("member-search");
const count = document.getElementById("member-count");
search.addEventListener("input", () => {
  query = search.value.trim().toLocaleLowerCase();
  selectedId = "";
  render();
});
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
}

function unique(list) {
  return [...new Set(list)].sort((a, b) => a.localeCompare(b));
}

function filteredMembers() {
  return members.filter((m) => {
    const tagOk = !activeTag || (m.expertise_tags || []).includes(activeTag);
    const countryOk = !activeCountry || m.country_code === activeCountry;
    const searchOk = !query || `${m.name} ${m.institution}`.toLocaleLowerCase().includes(query);
    return tagOk && countryOk && searchOk;
  });
}

function renderFilters() {
  const tags = unique(members.flatMap((m) => m.expertise_tags || []));
  const countries = unique(members.map((m) => m.country_code).filter(Boolean));

  tagFilters.innerHTML = `<button class="chip ${activeTag ? "" : "active"}" data-tag="">all expertise</button>` +
    tags.map((t) => `<button class="chip ${activeTag === t ? "active" : ""}" data-tag="${t}">${TAG_LABELS[t] || t}</button>`).join("");

  countryFilters.innerHTML = `<button class="chip ${activeCountry ? "" : "active"}" data-country="">all countries</button>` +
    countries.map((c) => `<button class="chip ${activeCountry === c ? "active" : ""}" data-country="${c}">${c}</button>`).join("");

  tagFilters.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeTag = btn.dataset.tag || "";
      selectedId = "";
      render();
    });
  });

  countryFilters.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeCountry = btn.dataset.country || "";
      selectedId = "";
      render();
    });
  });
}

function renderDetails(member) {
  if (!member) {
    details.classList.add("hidden");
    details.innerHTML = "";
    return;
  }

  member = Object.fromEntries(Object.entries(member).map(([key, value]) => [key, typeof value === "string" ? escapeHTML(value) : value]));
  details.classList.remove("hidden");
  details.innerHTML = `
    <h3>${member.name}</h3>
    <p>${member.institution}${member.country ? " · " + member.country : ""}</p>
    ${member.email ? `<p><strong>Work email:</strong> ${member.email}</p>` : ""}
    <p><strong>Expertise:</strong> ${member.expertise || "Not provided"}</p>
    <p><strong>Past work:</strong> ${member.past_works || "Not provided"}</p>
    <p><strong>Current interests:</strong> ${member.current_interests || "Not provided"}</p>
  `;
}

function renderCards(items) {
  board.innerHTML = "";

  for (const member of items) {
    const node = tpl.content.firstElementChild.cloneNode(true);
    node.dataset.id = member.id;
    node.tabIndex = 0;
    node.setAttribute("role", "button");
    node.setAttribute("aria-expanded", String(selectedId === member.id));
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        node.click();
      }
    });

    node.querySelector(".badge").textContent = member.domain_badge || "?";
    node.querySelector(".name").textContent = member.name;
    node.querySelector(".institution").textContent = member.institution || "Institution not set";
    node.querySelector(".meta").textContent = member.country || "";

    const tagsEl = node.querySelector(".tags");
    (member.expertise_tags || []).forEach((tag) => {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = TAG_LABELS[tag] || tag;
      span.style.background = TAG_COLOR[tag] || "#eaf4f8";
      tagsEl.appendChild(span);
    });

    if (selectedId === member.id) node.classList.add("selected");

    node.addEventListener("click", () => {
      selectedId = selectedId === member.id ? "" : member.id;
      render();
      [...board.children].find(card => card.dataset.id === member.id)?.focus({preventScroll: true});
    });

    board.appendChild(node);
  }
}

function render() {
  const items = filteredMembers();
  renderFilters();
  renderCards(items);
  count.textContent = `${items.length} of ${members.length} members`;
  if (!items.length) board.textContent = "No members match these filters.";

  const selected = items.find((m) => m.id === selectedId);
  renderDetails(selected);
}

async function init() {
  const response = await fetch("./data/members.json");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const payload = await response.json();
  members = payload.members || [];
  render();
}

init().catch((err) => {
  board.textContent = `Failed to load members data: ${err.message}`;
});
