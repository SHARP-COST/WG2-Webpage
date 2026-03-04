const board = document.getElementById("board");
const details = document.getElementById("details");
const linksSvg = document.getElementById("links");
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

function sharedScore(a, b) {
  const sa = new Set(a.expertise_tags || []);
  const sb = new Set(b.expertise_tags || []);
  let score = 0;
  for (const t of sa) if (sb.has(t)) score += 1;
  return score;
}

function unique(list) {
  return [...new Set(list)].sort((a, b) => a.localeCompare(b));
}

function filteredMembers() {
  return members.filter((m) => {
    const tagOk = !activeTag || (m.expertise_tags || []).includes(activeTag);
    const countryOk = !activeCountry || m.country_code === activeCountry;
    return tagOk && countryOk;
  });
}

function renderFilters() {
  const tags = unique(members.flatMap((m) => m.expertise_tags || []));
  const countries = unique(members.map((m) => m.country_code));

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

function renderDetails(member, connected) {
  if (!member) {
    details.classList.add("hidden");
    details.innerHTML = "";
    return;
  }

  details.classList.remove("hidden");
  details.innerHTML = `
    <h3>${member.name}</h3>
    <p>${member.institution || "Institution not set"} · ${member.country || "Unknown"}</p>
    <p><strong>Expertise:</strong> ${member.expertise || "Not provided"}</p>
    <p><strong>Past work:</strong> ${member.past_works || "Not provided"}</p>
    <p><strong>Current interests:</strong> ${member.current_interests || "Not provided"}</p>
    <p class="list"><strong>Connected members:</strong> ${connected.map((c) => c.name).join(", ") || "none"}</p>
  `;
}

function drawLinks(items, selected) {
  const rect = board.getBoundingClientRect();
  linksSvg.setAttribute("viewBox", `0 0 ${Math.max(1, rect.width)} ${Math.max(1, rect.height)}`);
  linksSvg.innerHTML = "";
  if (!selected) return;

  const selectedEl = board.querySelector(`[data-id="${selected.id}"]`);
  if (!selectedEl) return;

  const sa = selectedEl.getBoundingClientRect();
  const x1 = sa.left + sa.width / 2 - rect.left;
  const y1 = sa.top + sa.height / 2 - rect.top;

  for (const member of items) {
    if (member.id === selected.id) continue;
    const score = sharedScore(selected, member);
    if (score <= 0) continue;

    const el = board.querySelector(`[data-id="${member.id}"]`);
    if (!el) continue;

    const mb = el.getBoundingClientRect();
    const x2 = mb.left + mb.width / 2 - rect.left;
    const y2 = mb.top + mb.height / 2 - rect.top;

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", String(x1));
    line.setAttribute("y1", String(y1));
    line.setAttribute("x2", String(x2));
    line.setAttribute("y2", String(y2));
    line.setAttribute("stroke", "#1f6d8f");
    line.setAttribute("stroke-opacity", String(Math.min(0.9, 0.24 + score * 0.18)));
    line.setAttribute("stroke-width", String(0.6 + score * 0.7));
    linksSvg.appendChild(line);
  }
}

function renderCards(items) {
  board.innerHTML = "";

  for (const member of items) {
    const node = tpl.content.firstElementChild.cloneNode(true);
    node.dataset.id = member.id;

    node.querySelector(".badge").textContent = member.domain_badge || "?";
    node.querySelector(".name").textContent = member.name;
    node.querySelector(".institution").textContent = member.institution || "Institution not set";
    node.querySelector(".meta").textContent = `${member.country_code || "UN"} · ${member.email || "email missing"}`;

    const tagsEl = node.querySelector(".tags");
    (member.expertise_tags || []).forEach((tag) => {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = TAG_LABELS[tag] || tag;
      span.style.background = TAG_COLOR[tag] || "#eaf4f8";
      tagsEl.appendChild(span);
    });

    if (selectedId && selectedId !== member.id) {
      const selected = items.find((m) => m.id === selectedId);
      if (selected && sharedScore(selected, member) === 0) node.classList.add("dimmed");
    }
    if (selectedId === member.id) node.classList.add("selected");

    node.addEventListener("click", () => {
      selectedId = selectedId === member.id ? "" : member.id;
      render();
    });

    board.appendChild(node);
  }
}

function render() {
  const items = filteredMembers();
  renderFilters();
  renderCards(items);

  const selected = items.find((m) => m.id === selectedId);
  const connected = selected ? items.filter((m) => m.id !== selected.id && sharedScore(selected, m) > 0) : [];

  renderDetails(selected, connected);
  requestAnimationFrame(() => drawLinks(items, selected));
}

async function init() {
  const response = await fetch("./data/members.json");
  const payload = await response.json();
  members = payload.members || [];
  render();
  window.addEventListener("resize", () => {
    const items = filteredMembers();
    const selected = items.find((m) => m.id === selectedId);
    drawLinks(items, selected);
  });
}

init().catch((err) => {
  board.innerHTML = `<p>Failed to load members data: ${err.message}</p>`;
});
