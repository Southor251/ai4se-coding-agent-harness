const timeline = [
  { step: 1, state: "tool", label: "read_file README.md", meta: "permission=allow" },
  { step: 2, state: "pending", label: "write_file .harness/demo-note.txt", meta: "permission=ask hitl=pending" },
  { step: 3, state: "done", label: "Demo walkthrough loaded", meta: "permission=allow" },
];

document.querySelector("#timeline").innerHTML = timeline
  .map((item) => `<li class="${item.state}"><strong>Step ${item.step}</strong> ${item.label}<br><span>${item.meta}</span></li>`)
  .join("");

document.querySelector("#hitl-list").innerHTML = [
  '<div class="request"><strong>pending write_file</strong><p>Review .harness/demo-note.txt before execution.</p></div>',
].join("");
