---
up: "[[Template]]"
sticker: emoji//1f5d3-fe0f
---
## Weekly Report
## **🦐本週工作內容說明**


---
## **🐋時程調整**


---
## **🦒下週重點**




<%*
// Week note: normally created by the daily template inside
// Journal/<YYYY>/<YY_MM>/<n>/. If the Calendar plugin creates it somewhere else
// ("Week <n>"), place it by its ISO week number in the current week-year.
const self = tp.config.target_file;
const inTree = self.parent.path.match(/^Journal\/\d{4}\/(\d{2}_\d{2})\/\d+$/);
let month;
if (inTree) {
  month = inTree[1];
} else {
  const week = parseInt(tp.file.title.replace(/\D/g, ""), 10);
  const thursday = moment().isoWeek(week).isoWeekday(4).format("YYYY-MM-DD");
  const loc = await tp.user.journal_prepare(thursday);
  await tp.file.move(`${loc.folder}/${loc.weekNote}`);
  month = loc.month;
}

await tp.hooks.on_all_templates_executed(async () => {
  await app.fileManager.processFrontMatter(self, (fm) => {
    fm.sticker = "emoji//1f5d3-fe0f";
    fm.up = `[[${month}]]`;
  });
});
-%>
