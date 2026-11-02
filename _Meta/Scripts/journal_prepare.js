// Templater user script: tp.user.journal_prepare("YYYY-MM-DD")
//
// Journal layout: Journal/<YYYY>/<YY_MM>/<n>/<YYYY-MM-DD>.md + "Week <ISO week>.md"
//   - A week (Mon-Sun) belongs to the month of its Thursday (ISO 8601 rule),
//     so a week that crosses a month or year boundary stays in one folder.
//   - n = which Thursday of that month it is (1..5).
//
// Creates any missing folders plus the year note (<YYYY>.md) and month note
// (<YY_MM>.md), then returns where the daily note and week note belong.
async function journal_prepare(dateStr) {
    const day = window.moment(dateStr, "YYYY-MM-DD", true);
    if (!day.isValid()) {
        throw new Error(`journal_prepare: bad date "${dateStr}"`);
    }

    const thursday = day.clone().isoWeekday(4);
    const year = thursday.format("YYYY");
    const month = thursday.format("YY_MM");
    const n = Math.ceil(thursday.date() / 7);
    const week = day.isoWeek();

    const yearFolder = `Journal/${year}`;
    const monthFolder = `${yearFolder}/${month}`;
    const weekFolder = `${monthFolder}/${n}`;

    for (const folder of [yearFolder, monthFolder, weekFolder]) {
        if (!app.vault.getAbstractFileByPath(folder)) {
            await app.vault.createFolder(folder);
        }
    }

    // Folder notes for the Breadcrumbs tree: Journal <- year <- month <- Week
    const notes = [
        [`${yearFolder}/${year}.md`, "Journal", "lucide//calendar-days"],
        [`${monthFolder}/${month}.md`, year, "lucide//calendar-range"],
    ];
    for (const [path, up, sticker] of notes) {
        if (!app.vault.getAbstractFileByPath(path)) {
            await app.vault.create(path, `---\nup: "[[${up}]]"\nsticker: ${sticker}\n---\n`);
        }
    }

    return {
        date: day.format("YYYY-MM-DD"),
        year,
        month,
        n,
        week,
        weekNote: `Week ${week}`,
        folder: weekFolder,
    };
}

module.exports = journal_prepare;
