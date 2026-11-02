---
up: "[[Template]]"
sticker: emoji//1f4c5
---
## 🐳**Journal**


---
## 📅 **Today's Progress**


---
<%*
// Daily note: works from Obsidian's "Open today's daily note" button (creates
// Journal/<date>.md), from the Calendar plugin (any date), or from a blank note.
// It moves itself to Journal/<YYYY>/<YY_MM>/<n>/ and creates the week note,
// month note and year note if they are missing.
const self = tp.config.target_file;
const dateStr = moment(tp.file.title, "YYYY-MM-DD", true).isValid()
    ? tp.file.title
    : tp.date.now("YYYY-MM-DD");
const loc = await tp.user.journal_prepare(dateStr);
const target = `${loc.folder}/${loc.date}`;

// The native button only looks for Journal/<date>.md, so a second click makes
// a duplicate. Open the real note instead and remove the duplicate.
const existing = app.vault.getAbstractFileByPath(`${target}.md`);
if (existing && existing.path !== self.path) {
  await tp.hooks.on_all_templates_executed(async () => {
    await app.workspace.getLeaf(false).openFile(existing);
    await app.vault.delete(self);
  });
  return;
}

await tp.file.move(target);

if (!app.vault.getAbstractFileByPath(`${loc.folder}/${loc.weekNote}.md`)) {
  await tp.file.create_new(
    tp.file.find_tfile("_Meta/Template/Week .md"),
    loc.weekNote,
    false,
    app.vault.getAbstractFileByPath(loc.folder)
  );
}

await tp.hooks.on_all_templates_executed(async () => {
  const currentMoment = moment(loc.date, "YYYY-MM-DD");

  let prevMoment = currentMoment.clone().subtract(1, 'days');
  if (prevMoment.day() === 0) prevMoment.subtract(2, 'days'); // Sunday -> Friday
  else if (prevMoment.day() === 6) prevMoment.subtract(1, 'days'); // Saturday -> Friday

  let nextMoment = currentMoment.clone().add(1, 'days');
  if (nextMoment.day() === 6) nextMoment.add(2, 'days'); // Saturday -> Monday
  else if (nextMoment.day() === 0) nextMoment.add(1, 'days'); // Sunday -> Monday

  await app.fileManager.processFrontMatter(self, (fm) => {
    fm.sticker = "emoji//1f4c5";
    fm.up = loc.weekNote;
    fm.prev = prevMoment.format("YYYY-MM-DD");
    fm.next = nextMoment.format("YYYY-MM-DD");
  });
});
%>
