const fs = require("fs");
const path = require("path");

const researchDir = __dirname;
const atlasPath = path.join(researchDir, "content_atlas.json");
const atlas = JSON.parse(fs.readFileSync(atlasPath, "utf8"));
const videos = atlas.videos || [];
const signalTopic = Object.keys(atlas.topic_counts_multi_label || {}).find((name) => name.startsWith("CAT-SIGNAL"));

if (!signalTopic) {
  throw new Error("CAT-SIGNAL topic not found");
}

const signalVideos = videos.filter((video) => (video.dominant_topics || []).includes(signalTopic));

const mdPath = path.join(researchDir, "behavior-signal-lists.md");
const allCsvPath = path.join(researchDir, "content-signal-list-644.csv");
const signalCsvPath = path.join(researchDir, "cat-signal-behavior-list-142.csv");

function escapeMd(value) {
  return String(value ?? "")
    .replace(/\r?\n/g, " ")
    .replace(/\|/g, "\\|")
    .trim();
}

function escapeCsv(value) {
  const text = String(value ?? "").replace(/\r?\n/g, " ").trim();
  if (/[",\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

function topics(video) {
  return (video.dominant_topics || []).join(", ");
}

function row(video, number, includeScore = false) {
  const values = [
    number,
    video.index,
    video.id,
    video.title,
    video.duration_min,
    video.duration_band,
    video.series,
    topics(video),
    video.book_part_candidate,
    video.book_conversion,
    video.url
  ];

  if (includeScore) {
    values.splice(8, 0, video.topic_scores?.[signalTopic] ?? "");
  }

  return values;
}

function toCsv(rows, includeScore = false) {
  const headers = includeScore
    ? ["no", "atlas_index", "video_id", "title", "duration_min", "duration_band", "series", "topics", "cat_signal_score", "book_part_candidate", "book_conversion", "url"]
    : ["no", "atlas_index", "video_id", "title", "duration_min", "duration_band", "series", "topics", "book_part_candidate", "book_conversion", "url"];

  return "\ufeff" + [headers, ...rows].map((line) => line.map(escapeCsv).join(",")).join("\n") + "\n";
}

function mdTable(rows, includeScore = false) {
  const headers = includeScore
    ? ["No", "Atlas", "Video ID", "제목", "분", "구간", "시리즈", "주제", "행동점수", "책 파트 후보", "전환 방식", "URL"]
    : ["No", "Atlas", "Video ID", "제목", "분", "구간", "시리즈", "주제", "책 파트 후보", "전환 방식", "URL"];
  const divider = headers.map(() => "---");

  return [headers, divider, ...rows].map((line) => `| ${line.map(escapeMd).join(" | ")} |`).join("\n");
}

const allRows = videos.map((video, index) => row(video, index + 1));
const signalRows = signalVideos.map((video, index) => row(video, index + 1, true));
const topicSummary = Object.entries(atlas.topic_counts_multi_label || {})
  .map(([name, count]) => `| ${escapeMd(name)} | ${count} |`)
  .join("\n");

const md = `# 행동 신호 목록 분리 정리

생성일: 2026-06-04
기준 파일: \`research/content_atlas.json\`

## 요약

- 전체 비-Shorts 후보: ${atlas.total_non_shorts ?? videos.length}개
- 전체 후보 재생 시간: ${atlas.duration_hours ?? ""}시간
- \`${escapeMd(signalTopic)}\` 카테고리: ${signalVideos.length}개
- 주의: 랜딩 페이지에서 말한 \`644개\`는 행동 신호만의 개수가 아니라, Shorts를 제외한 전체 콘텐츠 후보 수다. 실제 행동 신호 카테고리는 아래 별도 목록의 ${signalVideos.length}개다.

## 주제별 개수

| 주제 | 개수 |
| --- | --- |
${topicSummary}

## 산출 파일

- \`content-signal-list-644.csv\`: 전체 644개 콘텐츠 신호 목록
- \`cat-signal-behavior-list-142.csv\`: CAT-SIGNAL 행동 신호 142개 목록
- 이 문서: 두 목록을 Markdown 표로 함께 확인하는 참조 문서

## CAT-SIGNAL 행동 신호 142개 목록

${mdTable(signalRows, true)}

## 전체 644개 콘텐츠 신호 목록

${mdTable(allRows, false)}
`;

fs.writeFileSync(mdPath, md, "utf8");
fs.writeFileSync(allCsvPath, toCsv(allRows, false), "utf8");
fs.writeFileSync(signalCsvPath, toCsv(signalRows, true), "utf8");

console.log(JSON.stringify({
  signalTopic,
  totalVideos: videos.length,
  behaviorSignalVideos: signalVideos.length,
  files: [
    mdPath,
    allCsvPath,
    signalCsvPath
  ]
}, null, 2));
